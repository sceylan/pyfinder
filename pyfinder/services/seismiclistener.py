# -*- coding: utf-8 -*-
# !/usr/bin/env python
""" 
Listener for the Seismic Portal WebSocket. This module listens to the Seismic Portal WebSocket 
and processes incoming messages. It filters messages based on region and magnitude criteria. 
The module uses Tornado for asynchronous I/O and logging for debugging and information purposes.    
"""

from __future__ import unicode_literals
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado import gen
import logging
import json
from pyfinderconfig import pyfinderconfig
from services.eventtracker import EventTracker
from utils.customlogger import file_logger

# WebSocket URI for Seismic Portal
echo_uri = pyfinderconfig["seismic-portal-listener"]["echo-uri"]

# Interval to ping the server to keep the connection alive
PING_INTERVAL = pyfinderconfig["seismic-portal-listener"]["ping-interval"]

# Logger
logger = file_logger(
    module_name="SeismicListener",
    log_file="seismiclistener.log",
    rotate=True,
    overwrite=False,
    level=logging.DEBUG
)
# Database tracker for event management
tracker = EventTracker("event_tracker.db", logger=logger)

# Filter for region
def is_event_in_region(event, target_regions):
    if isinstance(target_regions, str):
        target_regions = [target_regions]
    
    # Check if the target regions include 'all', 'world' or empty string
    for region in target_regions:
        if region.lower().strip() in ['all', 'world', '']:
            return True
        
    region = event.get('flynn_region', '')

    # Make all case-insensitive
    region = region.lower()
    target_regions = [r.lower() for r in target_regions]

    # Check if the region is in the target regions
    return any(target_region in region for target_region in target_regions)

# Filter for magnitude
def is_magnitude_above_threshold(event, min_magnitude):
    magnitude = event.get('mag', 0)
    
    if isinstance(magnitude, str):
        try:
            magnitude = float(magnitude)
        except ValueError:
            logger.error(f"Invalid magnitude value: {magnitude}")
            return False

    return magnitude >= min_magnitude

# Function to process incoming messages, applying filters
def myprocessing(message, target_regions=None, min_magnitude=0):
    try:
        data = json.loads(message)
        info = data['data']['properties']
        info['action'] = data['action']

        # Set default region filter if not provided
        if target_regions is None:
            target_regions = []

        logger.info(f"Received message: {info['unid']} with action: {info['action']}")
        logger.debug(f"Message data: {info}")

        # Check if event matches the region and magnitude criteria
        if not is_event_in_region(info, target_regions):
            logger.info(f"|- Desicion SKIP: Event {info['unid']} is outside the target regions, skipping...")
            return
        else:
            logger.info(f"|- Desicion KEEP: Event {info['unid']} is in the target regions: {target_regions}")

        if not is_magnitude_above_threshold(info, min_magnitude):
            logger.info(f"|- Desicion SKIP: Event {info['unid']} has magnitude {info['mag']} below threshold, skipping...")
            return
        else:
            logger.info(f"|- Desicion KEEP: Event {info['unid']} has magnitude {info['mag']} above threshold: {min_magnitude}")        
        
        logger.info(f"Final decision: PROCESS: Event {info['unid']} with action: {info['action']}")

        # Process new events
        if info['action'] == 'create':
            logger.info(f"New event: {info['unid']} at {info['time']}, Magnitude: {info['mag']}, Region: {info['flynn_region']}")
            tracker.register_event(
                event_id=info['unid'],
                services=["RRSM"],
                last_update_time=info['lastupdate'],
                origin_time=info['time'],
                expiration_days=5
            ) 

        # Process event updates
        elif info['action'] == 'update':
            logger.info(f"Updated event: {info['unid']} at {info['time']}, Magnitude: {info['mag']}, Region: {info['flynn_region']}")
            tracker.register_event_after_update(
                event_id=info['unid'],
                services=["RRSM"],
                new_last_update_time=info['lastupdate'],
                origin_time=info['time'],
                expiration_days=5
            )

    except Exception:
        logger.exception("Unable to process message")

@gen.coroutine
def listen(ws, target_regions=None, min_magnitude=0):
    while True:
        msg = yield ws.read_message()  # Read the message from WebSocket
        if msg is None:
            logger.info("WebSocket closed")
            break
        myprocessing(msg, target_regions=target_regions, min_magnitude=min_magnitude)  # Process the received message

@gen.coroutine
def launch_client(target_regions=None, min_magnitude=0):
    while True:
        try:
            logger.info("Opening WebSocket connection to %s", echo_uri)
            ws = yield websocket_connect(echo_uri, ping_interval=PING_INTERVAL)  # Establish WebSocket connection

            logger.info("WebSocket connection established. Waiting for messages...")
            yield listen(ws, target_regions=target_regions, min_magnitude=min_magnitude)  # Start listening for messages
        except Exception:
            logger.exception("Connection error")
            logger.info("Retrying connection in 5 seconds...")
            yield gen.sleep(5)


def start_emsc_listener():
    """ Start the Seismic Portal WebSocket listener service. """
    # Define the regions of interest and minimum magnitude
    if "seismic-portal-listener" not in pyfinderconfig:
        target_regions = ['world']
        min_magnitude = 3.0
    else:
        # Target region defaults to 'world' if not specified
        if "target-regions" not in pyfinderconfig["seismic-portal-listener"] or \
            not pyfinderconfig["seismic-portal-listener"]["target-regions"]:
            target_regions = ['world']
        else:
            target_regions = pyfinderconfig["seismic-portal-listener"]["target-regions"]
        
        # Minimum magnitude defaults to 3.0 if not specified
        if "min-magnitude" not in pyfinderconfig["seismic-portal-listener"] or \
            not pyfinderconfig["seismic-portal-listener"]["min-magnitude"]:
            min_magnitude = 3.0
        else:
            min_magnitude = pyfinderconfig["seismic-portal-listener"]["min-magnitude"]

    # Log the configuration
    logger.info(" ===== Starting Seismic Portal WebSocket listener =====")
    logger.info("Configuration:")
    logger.info("|- Target regions: %s", target_regions)
    logger.info("|- Minimum magnitude: %s", min_magnitude)
    logger.info("|- WebSocket URI: %s", echo_uri)
    

    # Start Tornado IOLoop
    logger.info("Starting Tornado IOLoop")
    ioloop = IOLoop.instance()

    # Launch WebSocket client with filters
    logger.info("Launching WebSocket client")
    # launch_client(target_regions=target_regions, min_magnitude=min_magnitude)
    ioloop.add_callback(launch_client, target_regions=target_regions, min_magnitude=min_magnitude)

    try:
        # Start the Tornado IOLoop
        logger.info("Starting the IOLoop ...")
        ioloop.start()  

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the IOLoop
        logger.info("Closing WebSocket")
        ioloop.stop()  


# Main function to start the service directly from this script
if __name__ == '__main__':
    # Start the service
    start_emsc_listener()    
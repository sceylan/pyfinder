# -*- coding: utf-8 -*-
# !/usr/bin/env python
""" Listener for the Seismic Portal WebSocket. """

from __future__ import unicode_literals
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop
from tornado import gen
import logging
import json
import sys
from pyfinderconfig import pyfinderconfig

# WebSocket URI for Seismic Portal
echo_uri = pyfinderconfig["seismic-portal-listener"]["echo-uri"]

# Interval to ping the server to keep the connection alive
PING_INTERVAL = pyfinderconfig["seismic-portal-listener"]["ping-interval"]

# Set up a new file logger
def file_logger(rotate=True):
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    
    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    # Handle all log levels
    ch.setLevel(logging.NOTSET)
    # Add ch to logger
    logger.addHandler(ch)

    # Create file handler and set level to debug
    mode = "a"
    if rotate:
        try:
            fh = logging.handlers.RotatingFileHandler(
                __name__, maxBytes=1000000, backupCount=7, 
                encoding='utf-8', mode=mode)
        except Exception as e:
            fh = logging.FileHandler(__name__, mode=mode, encoding='utf-8')
    else:
        fh = logging.FileHandler(__name__, mode=mode, encoding='utf-8')

    fh.setLevel(logging.NOTSET)
    
    return logger

logger = file_logger()

# Filter for region
def is_event_in_region(event, target_regions):
    if isinstance(target_regions, str):
        target_regions = [target_regions]
    
    # Check if the target regions include 'all' or 'world'
    for region in target_regions:
        if region.lower() in ['all', 'world']:
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
    return magnitude >= min_magnitude

# Function to process incoming messages, applying filters
def myprocessing(message, target_regions=None, min_magnitude=0):
    # Set up logging
    # file_logger()
    
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
            logger.info(f"Event {info['unid']} is outside the target regions, skipping...")
            return

        if not is_magnitude_above_threshold(info, min_magnitude):
            logger.info(f"Event {info['unid']} has magnitude {info['mag']} below threshold, skipping...")
            return

        # Process new events
        if info['action'] == 'create':
            logger.info(f"New event: {info['unid']} at {info['time']}, Magnitude: {info['mag']}, Region: {info['flynn_region']}")
            # TODO: Handle new event logic here 

        # Process event updates
        elif info['action'] == 'update':
            logger.info(f"Updated event: {info['unid']} at {info['time']}, Magnitude: {info['mag']}, Region: {info['flynn_region']}")
            # TODO: Handle event update logic here

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
    try:
        logger.info("Opening WebSocket connection to %s", echo_uri)
        ws = yield websocket_connect(echo_uri, ping_interval=PING_INTERVAL)  # Establish WebSocket connection
    except Exception:
        logger.exception("Connection error")
    else:
        logger.info("Waiting for messages...")
        listen(ws, target_regions=target_regions, min_magnitude=min_magnitude)  # Start listening for messages

if __name__ == '__main__':
    # Define the regions of interest and minimum magnitude
    target_regions = ["California", "Italy", "Japan", "Turkey"]  # Regions you care about
    min_magnitude = 4.0  # Minimum magnitude to process

    # Start Tornado IOLoop
    ioloop = IOLoop.instance()
    
    # Launch WebSocket client with filters
    launch_client(target_regions=target_regions, min_magnitude=min_magnitude)
    
    try:
        ioloop.start()  # Start the Tornado IOLoop
    except KeyboardInterrupt:
        logger.info("Closing WebSocket")
        ioloop.stop()  # Stop the IOLoop when interrupted

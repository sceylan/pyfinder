# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
Start services for the pyfinder module. 

This module is the main entry point for the pyfinder module. It starts the 
listeners to manage the whole workflow from a new event detection to running 
the FinDer with the parametric datasets.
"""
import os
import sys
# Add the parent directory to the system path
if not os.path.abspath("../") in sys.path:
    sys.path.insert(0, os.path.abspath("../"))

import threading
from services import seismiclistener
from services.scheduler import FollowUpScheduler
from utils.customlogger import file_logger

def start_services():
    logger = file_logger("monitoring.log", module_name="ServiceLauncher")

    # Start the seismic listener in a thread so it doesn't block
    def start_listener():
        logger.info("Starting seismic listener...")
        seismiclistener.start_emsc_listener()
    
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    # Start the follow-up scheduler in the main thread
    logger.info("Starting FollowUpScheduler...")
    scheduler = FollowUpScheduler()
    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        scheduler.shutdown()

""" The main execution module for the pyfinder module. """
if __name__ == "__main__":
    # Start the services
    start_services()
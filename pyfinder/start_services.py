# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
Start services for the pyfinder module. 

This module is the main entry point for the pyfinder module. It starts the 
listeners to manage the whole workflow from a new event detection to running 
the FinDer with the parametric datasets.
"""
from services import seismiclistener

def start_services():
    # Start the EMSC Seismic Portal WebSocket listener for the
    # firstquake web service.
    seismiclistener.start_emsc_listener()


""" The main execution module for the pyfinder module. """
if __name__ == "__main__":
    # Start the services
    start_services()
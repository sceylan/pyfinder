# -*- coding: utf-8 -*-
import os
import sys
from abc import abstractmethod

module_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(module_path)
sys.path.append(parent_dir)

from ..baseclient import BaseWebServiceClient


class ESMShakeMapClient(BaseWebServiceClient):
    """
    Class for ESM Shakemap web service client.

    As in the of each client, the class needs to override the following
    abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    """
    def __init__(self, agency="EMSC", base_url="https://esm-db.eu/esmws/", 
                 end_point="shakemap", version="1"):
        super().__init__(agency, base_url, end_point, version)

    def parse_response(self, file_like_obj):
        """ Parse the data returned by the web service. """
        pass

    def is_value_valid(self, option, value):
        """ 
        Check whether the given value is allowed for the given option. 
        The values for ESM shake map web service options are:
        (also see https://esm-db.eu//esmws/shakemap/1/query-options.html)

        eventid: 
            Select a specific event by ID. Multiple IDs are not allowed. 
            The event ID must exist in the catalog of your choice.
            
            Default: None
        
        catalog: 
            The catalog for the specified 'eventid'.
            Default: ESM
            Valid values: 'ESM', 'ISC', 'USGS', 'EMSC' and 'INGV'.

        format: 
            Output format for USGS ShakeMap program input. 
            Default: event_dat
            Valid values: 'event', 'event_dat' or 'event_fault'.	

        flag:	
            Include problematic data or not. Valid values are: '0' 
            (problematic data are not included) or 'all' (problematic 
            data are included and marked with flag="1" in event_dat output)
            Default: 0
            Valid values: '0' or 'all'

        encoding: 
            Character encoding of 'event_dat' output. This parameter 
            is ignored when output 'event' and 'event_fault' are chosen. 
            Default: UTF-8
            Valid values: 'UTF-8' or 'US-ASCII'	
        """
        # Check only the values of the options that are given below.
        # Event ID is not checked because it is not optional.
        options = {'catalog': ['ESM', 'ISC', 'USGS', 'EMSC', 'INGV'],
                   'format': ['event', 'event_dat', 'event_fault'],
                   'flag': ['0', 'all'], format: ['UTF-8', 'US-ASCII']}
    
        if option.lower() in options:
            if value not in options[option.lower()]:
                return False
        return True
            
    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service.
        """
        return ['eventid', 'catalog', 'format', 'flag', 'encoding']



    
# -*- coding: utf-8 -*-
import os
import sys
from abc import abstractmethod

module_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(module_path)
sys.path.append(parent_dir)

from ..baseclient import BaseWebServiceClient
from .shakemap_parser import ESMShakeMapParser

class ESMShakeMapClient(BaseWebServiceClient):
    """
    Class for ESM Shakemap web service client.

    As in the case for each client, the class needs to override 
    the following abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    - is_value_valid(self, option, value)
    """
    def __init__(self, agency="ESM", base_url="https://esm-db.eu/esmws/", 
                 end_point="shakemap", version="1"):
        super().__init__(agency, base_url, end_point, version)

        # The format of the output. The default is "event_dat".
        # If the format is "event", the output from the web service is
        # some basic event information such as location, magnitude, etc.
        # which requires another parser. This flag is used to determine
        # which parser to use. See the documentation of the web service 
        # for more details: 
        # https://esm-db.eu//esmws/shakemap/1/query-options.html
        self._format = "event_dat"

    def set_format(self, format):
        """ Set the format of the output."""
        self._format = format

    def get_format(self):
        """ Return the format of the output."""
        return self._format
    
    def parse_response(self, file_like_obj=None, options=None):
        """ Parse the data returned by the web service. """
        if 'format' not in options:
            # If format is not given, set it to "event_dat" by default.
            # It is also the default for the ESM ShakeMap web service.
            # This is to make sure that format is always given for parsers.
            options['format'] = "event_dat"

        if file_like_obj:
            parser = ESMShakeMapParser()

            # shakemap event_dat for amplitude data
            if options['format'] == "event_dat":
                data = parser.parse(file_like_obj)
            
            # shakemap event for event information
            elif options['format'] == "event":
                data = parser.parse_earthquake(file_like_obj)

            self.set_data(data)

        return self.get_data()

    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service.
        """
        return ['eventid', 'catalog', 'format', 'flag', 'encoding']

    def is_value_valid(self, option, value):
        """ 
        Check whether the given value is allowed for the given option. 
        The values for ESM shake map web service options are:
        (also see https://esm-db.eu//esmws/shakemap/1/query-options.html)

        eventid: 
            Select a specific event by ID. Multiple IDs are not allowed. 
            The event ID must exist in the catalog of your choice.
            Default: None
            Valid values: Any valid event ID that is in the database.

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

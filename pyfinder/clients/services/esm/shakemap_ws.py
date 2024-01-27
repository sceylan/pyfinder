# -*- coding: utf-8 -*-
import os
import sys
import urllib
# module_path = os.path.abspath(__file__)
# parent_dir = os.path.dirname(module_path)
# sys.path.append(parent_dir)
from ..basewebservice import BaseWebService
from .shakemap_parser import ESMShakeMapParser

class ESMShakeMapWebService(BaseWebService):
    """
    Class for ESM Shakemap web service client.

    As in the case for each client, the class needs to override 
    the following abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    - is_value_valid(self, option, value)
    - buld_url(self, **options)
    """
    def __init__(self, agency="ESM", base_url="https://esm-db.eu/esmws/", 
                 end_point="shakemap", version="1"):
        super().__init__(agency, base_url, end_point, version)

       
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

    def build_url(self, **options):
        """ 
        Return the final URL with web service, end point and options 
        combined. Also, keep it internally.
        """
        # Validate the options the first against the 
        # list of supported options
        options = self.validate_options(**options)

        # Safety check for the base URL. 
        if self.base_url and self.base_url[-1] != "/":
            self.base_url += "/"

        # Ensure the options dictionary is properly encoded as a 
        # URL-compatible string
        options = urllib.parse.urlencode(options, safe=':/?&=', 
                                         encoding='utf-8')
        
        # Combine the URL
        self.combined_url = \
            f"{self.base_url}{self.end_point}/{self.version}/query?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=', encoding='utf-8')
        
        return self.combined_url
    
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
                   'encoding': ['utf-8', 'UTF-8', 'us-ascii', 'US-ASCII'],
                   'flag': ['0', 'all']}
    
        if option.lower() in options:
            if value not in options[option.lower()]:
                return False
        return True

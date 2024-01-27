# -*- coding: utf-8 -*-
import urllib
from .shakemap_parser import RRSMShakeMapParser
from ..esm.shakemap_ws import ESMShakeMapWebService

class RRSMShakeMapWebService(ESMShakeMapWebService):
    """ 
    Class for RRSM shakemap web service client. This client 
    is similar to ESM shakemap client, but query has no options
    other than a compulsory eventid; hence, needs to be handled 
    slightly differently.

    It overrides these abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    - is_value_valid(self, option, value)
    - buld_url(self, **options)
    """
    def __init__(self, agency="ORFEUS", base_url="http://orfeus-eu.org/odcws/rrsm/", 
                 end_point="shakemap", version="1"):
        super().__init__(agency, base_url, end_point, version)

    def parse_response(self, file_like_obj=None, options=None):
        """ Parse the data returned by the web service. """
        if file_like_obj:
            parser = RRSMShakeMapParser()

            if 'type' in options and options['type'] == "event":
                data = parser.parse_earthquake(file_like_obj)
            else:
                data = parser.parse(file_like_obj)
            
            self.set_data(data)

        return self.get_data()
    
    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service. RRSM allows for only "eventid" and "type".
        """
        return ['eventid', 'type']
    
    def is_value_valid(self, option, value):
        """ 
        Normally checks whether the given value is allowed for 
        the given option. Since RRSM allows only "eventid" and "type", 
        always returns True. 
        """
        return True

    def build_url(self, **options):
        """ 
        RRSM uses inverted service and version order in the URL. Also,
        there is no "query" key word.
        e.g. http://orfeus-eu.org/odcws/rrsm/1/shakemap?eventid=20170524_0000045
        """
        if not options:
            options = {}
        
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
            f"{self.base_url}{self.version}/{self.end_point}?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=', encoding='utf-8')
        
        return self.combined_url
    
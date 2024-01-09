# -*- coding: utf-8 -*-
import urllib
from ..baseclient import BaseWebServiceClient

class MissingRequiredFieldError(Exception):
    """ Exception raised when a required field is missing. """
    pass

class EMSCFeltReportClient(BaseWebServiceClient):
    def __init__(self, agency='EMSC', end_point='api', version="1.1",
                 base_url='https://www.seismicportal.eu/testimonies-ws/'):
        super().__init__(agency, base_url, end_point, version)

    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service. RRSM allows for only "eventid".
        """
        return ['unids', 'includeTestimonies']
    
    def is_value_valid(self, option, value):
        """ 
        Checks for the value of includeTestimonies option only. 
        The options for EMSC are case sensitive.
        """
        options = {'includeTestimonies': ['true', 'false']}
    
        if option in options:
            if value not in options[option]:
                return False
        return True
    
    def build_url(self, **options):
        """ 
        Build the URL for the felt reports web service. 
        The URL structure is:
        http://www.seismicportal.eu/testimonies-ws/api/search?unids=[20201230_0000049]&includeTestimonies=true
        """
        if not options:
            options = {}
        
        # If a variation is passed by mistake, rename the keyword to 
        # 'includeTestimonies' as required by the EMSC. The naming 
        # is case sensitive.
        for combination in ['includetestimonies', 'IncludeTestimonies', 
                            'Includetestimonies']:
            if combination in options:
                value = options.pop(combination)
                options['includeTestimonies'] = value

        # Validate the options the first against the 
        # list of supported options
        options = self.validate_options(**options)
        
        # Safety check for the base URL. 
        if self.base_url and self.base_url[-1] != "/":
            self.base_url += "/"

        # Ensure the options dictionary is properly encoded as a 
        # URL-compatible string
        options = urllib.parse.urlencode(options)

        # Combine the URL
        self.combined_url = \
            f"{self.base_url}{self.end_point}/search?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=', encoding='utf-8')
        
        return self.combined_url
    
    def parse_response(self, file_like_obj=None, options=None):
        pass
# -*- coding: utf-8 -*-
import urllib
from ..basewebservice import BaseWebService, InvalidOptionValue
from .feltreport_parser import EMSCFeltReportParser

class MissingRequiredFieldError(Exception):
    """ Exception raised when a required field is missing. """
    pass

class EMSCFeltReportWebService(BaseWebService):
    """
    Class for EMSC felt report web service client.

    It overrides the following abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    - is_value_valid(self, option, value)
    - buld_url(self, **options)
    """
    def __init__(self, agency='EMSC', end_point='api', version="1.1",
                 base_url='https://www.seismicportal.eu/testimonies-ws/'):
        super().__init__(agency, base_url, end_point, version)

    def get_supported_options(self):
        """ 
        Return the list of options available at the EMSD felt reports 
        web service. RRSM allows for only "eventid".
        """
        return ['unids', 'includeTestimonies']
    
    def is_value_valid(self, option, value):
        """ 
        Checks for the value of includeTestimonies option only. 
        The options for EMSC are case sensitive.
        """
        _options = {'includeTestimonies': ['true', 'false']}
    
        if option in _options:
            if value not in _options[option]:
                return False
        return True
    
    def build_url(self, **options):
        """ 
        Build the URL for the felt reports web service. 
        The URL structure is:
        http://www.seismicportal.eu/testimonies-ws/api/search?unids=[20201230_0000049]&includeTestimonies=true
        """
        if not options:
            # If options are not defined, create an empty dict.
            # No options means we will query the whole event database
            # from the EMSC for the event information. The service
            # will return 500 records by default.
            options = {}
        
        # If a variation is passed by mistake, rename the keyword to 
        # 'includeTestimonies' as required by the EMSC. The naming 
        # is case sensitive.
        for combination in ['includetestimonies', 'IncludeTestimonies', 
                            'Includetestimonies']:
            if combination in options:
                value = options.pop(combination)
                options['includeTestimonies'] = value

        # Check for the "unids" option. It needs to passed as a list.
        # If it is a string, convert it to a string representation of 
        # a list. The web service expects the event id to be in brackets.
        if 'unids' in options:
            if isinstance(options['unids'], str): 
                # Check if the option string is already in a list 
                # format on both ends.
                if options['unids'][0] != '[':
                    options['unids'] = '[' + options['unids']
                if options['unids'][-1] != ']':    
                    options['unids'] = options['unids'] + ']'
            
                # Clean up white spaces and quotes that may have been
                # added by mistake.
                options['unids'] = options['unids'].replace(' ', '')
                options['unids'] = options['unids'].replace("'", '')
                options['unids'] = options['unids'].replace('"', '')

            elif isinstance(options['unids'], list):
                pass
            
            else:
                raise InvalidOptionValue("unids", options['unids'])    

        # Validate the options the first against the 
        # list of supported options
        options = self.validate_options(**options)
        
        # Safety check for the base URL. 
        if self.base_url and self.base_url[-1] != "/":
            self.base_url += "/"

        # Ensure the options dictionary is properly encoded as a 
        # URL-compatible string
        options = urllib.parse.urlencode(options, safe=':/?&=[]', 
                                         encoding='utf-8')

        # Combine the URL
        self.combined_url = \
            f"{self.base_url}{self.end_point}/search?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        # Note that we also need allow the square brackets in the URL.
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=[]', encoding='utf-8')
        
        return self.combined_url
    
    
    def parse_response(self, file_like_obj=None, options=None):
        """ Parse the response from felt reports web service. """
        # Check if testimonies are requested. The default 
        # on the web service is False.
        if 'includeTestimonies' in options:
            if options['includeTestimonies'].lower() == 'true':
                testimonies_included = True
            else:
                testimonies_included = False
        else:
            testimonies_included = False

        if file_like_obj:
            parser = EMSCFeltReportParser()

            if testimonies_included:
                # Intensity data with testimonies. This will be a zip 
                # file containing the intensity data in csv format.
                data = parser.parse_testimonies(file_like_obj)
                
            else:
                # Event information without testimonies. 
                # This will be in json format.
                data = parser.parse(file_like_obj)
            
            self.set_data(data)

        return self.get_data()

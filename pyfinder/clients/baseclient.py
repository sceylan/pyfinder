# -*- coding: utf-8 -*-
""" Base class for the web service clients. """
from abc import ABCMeta, abstractmethod
import urllib
import urllib.request as urllib_request
from . import http

class InvalidQueryOption(Exception):
    pass

class BaseWebServiceClient(ABCMeta):
    def __init__(self, agency=None, base_url=None, end_point=None, version="1"):
        # The web service base URL, e.g. "https://esm-db.eu/fdsnws"
        self.base_url = base_url

        # The web service end point, e.g. "shakemap"
        self.end_point = end_point

        # The web service version, e.g. "1"
        self.version = version

        # Full combined URL
        self.combined_url = self.build_url()

        # The agency providing the web service, e.g. "ESM"
        self.agency = agency

        # The data structure used to store the data retrieved from 
        # the web service. This will be a subclass of BaseDataStructure.
        self.data = None

    def get_data(self):
        """ Return the data structure."""
        return self.data
    
    def set_data(self, data):
        """ Set the data structure."""
        self.data = data

    def get_agency(self):
        """ Return the agency providing the web service."""
        return self.agency  
    
    def set_agency(self, agency):
        """ Set the agency providing the web service."""
        self.agency = agency

    def get_version(self):
        """ Return the web service version."""
        return self.version
    
    def set_version(self, version):
        """ Set the web service version."""
        self.version = version

    def get_end_point(self):
        """ Return the web service end point."""
        return self.end_point
    
    def set_end_point(self, end_point):
        """ Set the web service end point."""
        self.end_point = end_point

    def get_base_url(self):
        """ Return the web service base URL."""
        return self.base_url    
    
    def set_base_url(self, base_url):
        """ Set the web service base URL."""
        # Complete the base URL if it does not end with a slash
        if base_url and base_url[-1] != "/":
            base_url += "/"

        self.base_url = base_url

    def build_url(self, **options):
        """ 
        Return the final URL with web service, end point and options 
        combined. Also, keep it internally.
        """
        # Ensure the options dictionary is properly encoded as a 
        # URL-compatible string
        options = urllib.parse.urlencode(options)

        # Merge the URL with the options, service version and end point
        self.combined_url = f"{self.base_url}{self.end_point}
                              {self.version}/query?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=', encoding='utf-8')
        
        return self.combined_url
    
    
    def query(self, user=None, password=None, **options):
        """ Query the web service. """
        # Validate the options the first against the 
        # list of supported options
        self.validate_options(**options)

        # Combine a URL including the options
        url = self.build_url(**options)

        # The code below is taken from obspy.
        # Only add the authentication handler if required.
        handlers = []
        
        if user is not None and password is not None:
            # Create an OpenerDirector for HTTP Digest Authentication
            password_mgr = urllib_request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.base_url, user, password)
            handlers.append(urllib_request.HTTPDigestAuthHandler(password_mgr))

        if (user is None and password is None) or self._force_redirect is True:
            # Redirect if no credentials are given or the force_redirect
            # flag is True.
            handlers.append(http.CustomRedirectHandler())
        else:
            handlers.append(http.NoRedirectionHandler())
        opener = urllib_request.build_opener(*handlers)

        code, url_response = self.open_url(url=url, opener=opener)
        if code != 400:
            return self.parse(file_like_obj=url_response)

    @abstractmethod
    def parse(self, file_like_obj):
        """ Parse the data returned by the web service. """
        pass

    @abstractmethod
    def get_supported_options(self):
        """ Return the list of supported options for the web service. """
        return []

    def validate_options(self, **options):
        """
        Checks whether all the given options are supported by the relevant
        web service. Each subclass of this class is required supply a list
        of the options via the get_supported_ws_options() abstract method.
        """
        for option in options:
            if option not in self.get_supported_options():
                raise InvalidQueryOption(
                    "`{}` is not a valid query option for {}-{}".format(
                        option, self.get_agency(), self.get_web_service()))
            
    def open_url(self, url, opener):
        """ Download the data from the given URL using the opener. """
        try:
            code = url_response.getcode()
            url_response = opener.open(url)
        except urllib.error.HTTPError as e:
            code = e.code
            url_response = e
        except urllib.error.URLError as e:
            code = 400
            url_response = e
        except Exception as e:
            code = 400
            url_response = e
        return code, url_response
    
    

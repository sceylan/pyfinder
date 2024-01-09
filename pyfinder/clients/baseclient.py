# -*- coding: utf-8 -*-
""" Base class for the web service clients. """
from abc import ABC, abstractmethod
import urllib
import urllib.request as urlrequest
from urllib.parse import urlparse
from . import http

class InvalidQueryOption(Exception):
    """ Raised when the given option is not supported."""
    pass

class InvalidOptionValue(ValueError):
    """ Raised when the given option value is not allowed."""
    pass

class BaseWebServiceClient(ABC):
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

        # The data structure (model) to store the data retrieved from 
        # the web services. This will be a subclass of BaseDataStructure,
        # and mostly likely nested. 
        self.data = None

        # The flag to force redirect. If True, the client will follow
        # the redirect even if the credentials are given.
        self._force_redirect = False

    def set_force_redirect(self, force_redirect):
        """ Set the flag to force redirect. """
        self._force_redirect = force_redirect

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
            f"{self.base_url}{self.end_point}/{self.version}/query?{options}" 
        
        # Encode the URL to make it safe for HTTP requests
        self.combined_url = urllib.parse.quote(
            self.combined_url, safe=':/?&=', encoding='utf-8')
        
        return self.combined_url
    
    def query(self, url=None, user=None, password=None, **options):
        """ 
        Query the web service. If url is given, use it. Otherwise,
        build the URL using the options. The URL is not validated against
        the list of supported options, assuming that it is already built
        using the 
        >>> self.build_url(**options) 
        method.
        """
        # If URL is not given, combine one using the options
        if url is None:
            # First remove the unsupported options
            delete_these = []
            for key in options.keys():
                if not key in self.get_supported_options():
                    delete_these.append(key)
            
            # Now remove the unsupported options.
            for key in delete_these:
                del options[key]

            # Build the URL
            url = self.build_url(**options)
        
        # If URL is given, parse it to get the options
        else:
            parsed_url = urlparse(url)
            query_dict = urllib.parse.parse_qs(parsed_url.query)
            
            # Get the options from the query dictionary, but do not
            # include the unsupported options
            options = {key: value[0] \
                       for key, value in query_dict.items() \
                        if key in self.get_supported_options()}
            
            # Build the URL again with cleaned options
            url = self.build_url(**options)
  
        # The code below is taken from obspy.
        # Only add the authentication handler if required.
        handlers = []
        
        if user is not None and password is not None:
            # Create an OpenerDirector for HTTP Digest Authentication
            password_mgr = urlrequest.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.base_url, user, password)
            handlers.append(urlrequest.HTTPDigestAuthHandler(password_mgr))

        if (user is None and password is None) or self._force_redirect is True:
            # Redirect if no credentials are given or the force_redirect
            # flag is True.
            handlers.append(http.CustomRedirectHandler())
        else:
            handlers.append(http.NoRedirectionHandler())
        
        # Open the URL and get the response
        opener = urlrequest.build_opener(*handlers)
        code, url_response, error = self.open_url(url=url, opener=opener)
        
        if url_response is not None and \
            code not in [400, 404, 500, 501, 502, 503]:
            # If the code is not one of the HTTP errors or 404 (no data), 
            # parse the response
            return code, self.parse_response(
                file_like_obj=url_response, options=options)
        else:
            # If failed, return the code and None
            return code, None
        
    @abstractmethod
    def parse_response(self, file_like_obj):
        """ Parse the data returned by the web service. """
        pass

    @abstractmethod
    def get_supported_options(self):
        """ Return the list of supported options for the web service. """
        return []

    @abstractmethod
    def is_value_valid(self, option, value):
        """ 
        Validate the given option value. Each subclass of this class is
        required supply a list of the values per option. 
        """
        return True

    def validate_options(self, **options):
        """
        Check whether all the given options are supported by the relevant
        web service. Each subclass of this class is required supply a list
        of the options via the get_supported_ws_options() abstract method.
        """
        if options is None:
            return
        
        # Remove the unsupported options
        delete_these = []
        for key in options.keys():
            if not key in self.get_supported_options():
                delete_these.append(key)

        for key in delete_these:
            del options[key]

        # Validate the options again for sanity
        for option in options:
            if option not in self.get_supported_options():
                raise InvalidQueryOption(
                    "`{}` is not a valid query option for {}-{}".format(
                        option, self.get_agency(), self.get_end_point()))
            
            # Validate the option value
            else:
                if not self.is_value_valid(option, options[option]):
                    raise InvalidOptionValue(
                        "`{}` is not a valid value for `{}` option.".format(
                            options[option], option))
        return options
    
    def open_url(self, url, opener):
        """ 
        Open the given URL using the opener. Return HTTP return code, 
        the response, and the error, if any. A combination of the error
        code and response might provide more granular information about
        the error in subclasses.
        """
        try:
            url_response = opener.open(url)
            code = url_response.getcode()
            error = None
        except urllib.error.HTTPError as e:
            code = e.code
            url_response = None
            error = e
        except urllib.error.URLError as e:
            code = 400
            url_response = None
            error = e
        except Exception as e:
            code = 400
            url_response = None
            error = e

        # return the code, response and error, if any    
        return code, url_response, error
    
# -*-coding: utf-8 -*-
from .base_client import BaseClient, MissingRequiredOption
from .services import RRSMShakeMapWebService, RRSMPeakMotionWebService

class RRSMPeakMotionClient(BaseClient):
    """ 
    This class encapsulates the worker class for the RRSM peak motion 
    web service and its data structure(s). 
    
    The RRSM peak motion web service works with an event id:
    http://orfeus-eu.org/odcws/rrsm/1/peak-motion?eventid=20170524_0000045
    """
    def __init__(self):
        super().__init__()

        # Provider
        self.agency = "ORFEUS"
        
        # Main service url
        self.base_url = "http://orfeus-eu.org/odcws/rrsm/"
        
        # Query end point
        self.end_point = "peak-motion" 
        
        # Version of the service, if applicable
        self.version = "1"
        
        # Options for querying the amplitude data.
        self.amplitude_options = {'eventid': None}

        # Options for querying the event data.
        self.event_options = {'eventid': None}
        
        # Initialize the web service client.
        if self.get_web_service() is None:
            self.create_web_service()
                
    def set_event_id(self, event_id):
        """ Set the event id. """
        self.event_options['eventid'] = event_id
        self.amplitude_options['eventid'] = event_id

    def get_event_id(self):
        """ Return the event id. """
        return self.amplitude_options['eventid']
    
    def get_station_codes(self):
        """ Return the station codes. """
        return self.amplitude_data.get_station_codes()
    
    def get_stations(self):
        return self.amplitude_data.get_stations()
    
    def create_web_service(self)->RRSMPeakMotionWebService:
        """ Creates a new ESM shakemap web service client. """
        self.ws_client = RRSMPeakMotionWebService(
            agency=self.agency, base_url=self.base_url, 
            end_point=self.end_point, version=self.version)

        # Return the client for further use in case
        # the method is called directly.
        return self.ws_client
    
    def query(self, event_id=None, **other_options):
        """ Query the web service for earthquake information. """
        # Check and set options that are free to modify.
        # Leave 'encoding' as is. 'format' is already set
        # for different data sets.
        if event_id is not None:
            self.set_event_id(event_id)
        else:
            raise MissingRequiredOption(
                "Missing required option: event_id")
        
        # Query the web service for the event information. No need to
        # query twice for amplitudes. RRSM peak motion already returns 
        # a json with the station amplitudes and event parameters. 
        _url = self.ws_client.build_url(**self.event_options)
        _code, _peakmotion_data = self.ws_client.query(url=_url)
        self.set_event_data(_peakmotion_data)
        self.set_station_amplitudes(_peakmotion_data)
        
        # Return the response code and the data.
        # The amplitude data is the same as the event data for this client.
        return _code, _peakmotion_data, _peakmotion_data
              

class RRSMShakeMapClient(BaseClient):
    """ 
    This class encapsulates the worker class for the RRSM shakemap 
    web service and its data structure(s). 
    
    The RRSM shakemap web service is the same as ESM shakemap web service, 
    but there are fewer options: The event information is queried with 
    `type=event` instead of `format=event` as was the case for ESM web 
    services. 
    e.g. http://orfeus-eu.org/odcws/rrsm/1/shakemap?eventid=20240118_0000062&type=event
    """
    def __init__(self):
        super().__init__()

        # Provider
        self.agency = "ORFEUS"
        
        # Main service url
        self.base_url = "http://orfeus-eu.org/odcws/rrsm/"
        
        # Query end point
        self.end_point = "shakemap" 
        
        # Version of the service, if applicable
        self.version = "1"
        
        # Options for querying the amplitude data.
        self.amplitude_options = {'eventid': None}

        # Options for querying the event data.
        self.event_options = {'eventid': None, 'type': 'event'}
        
        # Initialize the web service client.
        if self.get_web_service() is None:
            self.create_web_service()
                
    def set_event_id(self, event_id):
        """ Set the event id. """
        self.event_options['eventid'] = event_id
        self.amplitude_options['eventid'] = event_id

    def get_event_id(self):
        """ Return the event id. """
        return self.amplitude_options['eventid']
    
    def get_station_codes(self):
        """ Return the station codes. """
        return self.amplitude_data.get_station_codes()
    
    def get_stations(self):
        return self.amplitude_data.get_stations()
    
    def create_web_service(self)->RRSMShakeMapWebService:
        """ Creates a new ESM shakemap web service client. """
        self.ws_client = RRSMShakeMapWebService(
            agency=self.agency, base_url=self.base_url, 
            end_point=self.end_point, version=self.version)

        # Return the client for further use in case
        # the method is called directly.
        return self.ws_client
    
    def query(self, event_id=None, **other_options):
        """ Query the web service for earthquake information. """
        # Check and set options that are free to modify.
        # Leave 'encoding' as is. 'format' is already set
        # for different data sets.
        if event_id is not None:
            self.set_event_id(event_id)
        else:
            raise MissingRequiredOption(
                "Missing required option: event_id")
        
        # Override the default `type` option with the 
        # other_options['type'] option if it is provided.
        if 'type' in other_options:
            self.event_options['type'] = other_options['type']

        # Query the web service for the event information.
        _url = self.ws_client.build_url(**self.event_options)
        _code, _event_data = self.ws_client.query(url=_url)
        self.set_event_data(_event_data)

        # Query the web service for the amplitude data.
        _url = self.ws_client.build_url(**self.amplitude_options)
        _code, _amplitude_data = self.ws_client.query(url=_url)
        self.set_station_amplitudes(_amplitude_data)

        # Return the response code and the data.
        return _code, _event_data, _amplitude_data


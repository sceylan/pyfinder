# -*-coding: utf-8 -*-
from .base_client import BaseClient, MissingRequiredOption
from .services import RRSMShakeMapWebService

class RRSMShakeMapClient(BaseClient):
    """ 
    This class encapsulates the worker class for the RRSM shakemap 
    web service and its data structure(s). The RRSM shakemap web 
    service is the same as ESM shakemap web service, but there are 
    fewer options: There is no event information query, but only the
    station amplitudes.
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
        
        # Initialize the web service client.
        if self.get_web_service() is None:
            self.create_web_service()
                
    def set_event_id(self, event_id):
        """ Set the event id. """
        self.amplitude_options['eventid'] = event_id

    def get_event_id(self):
        """ Return the event id. """
        return self.amplitude_options['eventid']
    
    def get_station_codes(self):
        """ Return the station codes. """
        return self.amplitude_data.get_station_codes()
    
    def get_stations(self):
        return self.amplitude_data.get_stations()
    
    def create_web_service(self):
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
        
        # Query the web service for the amplitude data.
        _url = self.ws_client.build_url(**self.amplitude_options)
        _code, _data = self.ws_client.query(url=_url)
        self.set_amplitudes(_data)

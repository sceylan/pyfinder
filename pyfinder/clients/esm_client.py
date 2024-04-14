# -*-coding: utf-8 -*-
from .base_client import BaseClient, MissingRequiredOption
from .services import ESMShakeMapWebService

class ESMShakeMapClient(BaseClient):
    """ 
    This class encapsulates the actual ESM shakemap web service 
    client and respective data structure(s). The purpose of this 
    class is to provide a single interface to the ESM web services. 
    The client classes are defined in the clients/services directory.
    """
    def __init__(self):
        super().__init__()

        # Provider
        self.agency = "ESM"
        
        # Main service url
        self.base_url = "https://esm-db.eu/esmws/"
        
        # Query end point
        self.end_point = "shakemap" 
        
        # Version of the service, if applicable
        self.version = "1"

        # Options for querying the event data.
        self.event_options = {'eventid': None, 'catalog': 'EMSC', 
                              'format': 'event', 'flag': '0', 
                              'encoding': 'UTF-8'}
        
        # Options for querying the amplitude data.
        self.amplitude_options = {'eventid': None, 'catalog': 'EMSC', 
                                  'format': 'event_dat', 'flag': '0', 
                                  'encoding': 'UTF-8'}
        
        # Initialize the web service client.
        if self.get_web_service() is None:
            self.create_web_service()
                
    def set_event_id(self, event_id):
        """ Set the event id. """
        self.event_options['eventid'] = event_id
        self.amplitude_options['eventid'] = event_id

    def get_event_id(self):
        """ Return the event id. """
        return self.event_options['eventid']
    
    def get_station_codes(self):
        """ Return the station codes. """
        return self.amplitude_data.get_station_codes()
    
    def get_stations(self):
        return self.amplitude_data.get_stations()
    
    def get_supported_catalogs(self):
        """ Return the list of supported catalogs. """
        return ['ESM', 'ISC', 'USGS', 'EMSC', 'INGV']
    
    def set_catalog(self, catalog):
        """ Set the catalog. Always defaults to EMSC when 
        the catalog is not supported. This is the same
        behavior as in the ESM web service. """
        if catalog not in self.get_supported_catalogs():
            catalog = 'EMSC'

        self.event_options['catalog'] = catalog
        self.amplitude_options['catalog'] = catalog

    def include_problematic_data(self, include=False):
        """ 
        Include problematic data in the output. The default is False.
        The default in the options for are also False (flag=0)
        """
        # Accept the actual value of the 'flag' option
        # as defined from the method interface.
        if isinstance(include, str):
            if include.lower() == 'all':
                include = True
            else:
                include = False

        # Set the 'flag' option
        if include:
            self.event_options['flag'] = 'all'
            self.amplitude_options['flag'] = 'all'
        else:
            self.event_options['flag'] = '0'
            self.amplitude_options['flag'] = '0'
        
    def create_web_service(self)->ESMShakeMapWebService:
        """ Creates a new ESM shakemap web service client. """
        self.ws_client = ESMShakeMapWebService(
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
        
        if 'catalog' in other_options:
            self.set_catalog(other_options['catalog'])

        if 'flag' in other_options:
            self.include_problematic_data(other_options['flag'])

        # Query the web service for the event information.
        _url = self.ws_client.build_url(**self.event_options)
        _code, _event_data = self.ws_client.query(url=_url)
        self.set_event_data(_event_data)

        # Now query the web service for the amplitude data.
        _url = self.ws_client.build_url(**self.amplitude_options)
        _code, _amplitude_data = self.ws_client.query(url=_url)
        self.set_station_amplitudes(_amplitude_data)

        # Return the code and data from the last query.
        return _code, _event_data, _amplitude_data
    
# -*-coding: utf-8 -*-
from abc import ABC, abstractmethod
from .services import BaseWebService
from .services.basedatastructure import BaseDataStructure

class MissingRequiredOption(ValueError):
    """ 
    Exception for missing required options. 
    """
    pass

class BaseClient(ABC):
    """ 
    Base class for the other classes that encapsulate the actual 
    web service clients. The purpose of this class is to provide a
    single interface to the web services. The client classes are
    defined in the clients/services directory.
    """
    def __init__(self):
        # The actual client for the ESM shakemap web service.
        self.ws_client:BaseWebService = None

        # Event parameters from the shakemap format=event option.
        self.event_data: BaseDataStructure = None

        # Amplitudes from the shakemap format=event_dat option,
        # or intensities from EMSC felt reports.
        self.amplitude_data: BaseDataStructure = None

    @abstractmethod
    def create_web_service(self):
        """ 
        Create a web service client. Should be implemented by the
        child classes.
        """
        return None

    @abstractmethod    
    def query(self, **options):
        """ Query the web service. """
        pass

    def set_agency(self, agency):
        """ Set the agency for the web service. """
        self.ws_client.set_agency(agency)

    def set_version(self, version):
        """ Set the version for the web service. """
        self.ws_client.set_version(version)

    def set_end_point(self, end_point):
        """ Set the service end point for the web service. """
        self.ws_client.set_end_point(end_point) 

    def set_base_url(self, base_url):
        """ Set the base url for the web service. """
        self.ws_client.set_base_url(base_url)   

    def set_event_data(self, event_data):
        """ Set the event information. """
        self.event_data = event_data

    def set_station_amplitudes(self, amplitude_data):
        """ 
        Set the amplitudes or intensities. Same as set_feltreports(), but included 
        for clarity. Both use the same attribute for storing the data.
        """
        self.amplitude_data = amplitude_data

    def set_feltreports(self, amplitude_data):
        """ 
        Set the amplitudes or intensities. Same as set_amplitudes(), but included 
        for clarity. Both use the same attribute for storing the data.
        """
        self.amplitude_data = amplitude_data

    def get_web_service(self):
        """ Get the web service client. """
        return self.ws_client
    
    def get_url(self):
        """ Return the combined URL (base + options) for the web service. """
        return self.ws_client.get_combined_url()
    
    def get_agency(self):
        """ Get the agency for the web service. """
        return self.ws_client.get_agency()
    
    def get_version(self):
        """ Get the version for the web service. """
        return self.ws_client.get_version()
    
    def get_end_point(self):
        """ Get the end point for the web service. """
        return self.ws_client.get_end_point()
    
    def get_base_url(self):
        """ Get the base url for the web service. """
        return self.ws_client.get_base_url()
        
    def get_event_data(self):
        """ Return the event information. """
        return self.event_data
    
    def get_station_amplitudes(self):
        """ Return the amplitudes or intensities. """
        return self.amplitude_data    

    def get_feltreports(self):
        """ 
        Return the amplitudes or intensities. Same as 
        get_amplitudes(), but included for clarity.
        """
        return self.amplitude_data        
    
# -*-coding: utf-8 -*-
from abc import ABC, abstractmethod

class BaseClient(ABC):
    """ 
    Base class for the other classes that encapsulate the actual 
    web service clients. The purpose of this class is to provide a
    single interface to the web services. The client classes are
    defined in the clients/services directory.
    """
    def __init__(self):
        # The actual client for the ESM shakemap web service.
        self.ws_client = self.create_web_service()

        # Event parameters from the shakemap format=event option.
        self.event_data = None

        # Amplitudes from the shakemap format=event_dat option.
        self.amplitude_data = None

    @abstractmethod
    def create_web_service(self):
        """ 
        Create a web service client. Should be implemented by the
        child classes.
        """
        return None
        
    def set_agency(self, agency):
        """ Set the agency for the web service. """
        self.ws_client.set_agency(agency)

    def set_version(self, version):
        """ Set the version for the web service. """
        self.ws_client.set_version(version)

    def set_end_point(self, end_point):
        """ Set the end point for the web service. """
        self.ws_client.set_end_point(end_point) 

    def set_base_url(self, base_url):
        """ Set the base url for the web service. """
        self.ws_client.set_base_url(base_url)   

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
    
    def get_data(self):
        """ Get the data from the web service. """
        return self.ws_client.get_data()
    
    def get_event_data(self):
        """ Get the event id from the web service. """
        return self.event_data
    
    def get_amplitude_data(self):
        """ Get the event id from the web service. """
        return self.amplitude_data        
    
    def query(self, **kwargs):
        """ Query the web service. """
        pass

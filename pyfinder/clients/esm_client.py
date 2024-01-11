# -*-coding: utf-8 -*-
from .base_client import BaseClient
from .services import ESMShakeMapWebService

class ESMShakeMapClient(BaseClient):
    """ 
    This class encapsulates the actual ESM shakemap web service 
    client and respective data structure(s). The purpose of this 
    class is to provide a single interface to the ESM web services. 
    The client classes are defined in the clients/services directory.
    """
    def __init__(self):
        # Provider
        self.agency = "ESM"
        
        # Main service url
        self.base_url = "https://esm-db.eu/esmws/"
        
        # Query end point
        self.end_point = "shakemap" 
        
        # Version of the service, if applicable
        self.version = "1"

        # Initialize the web service client.
        self.create_web_service()

        # Call the parent constructor at the end.
        super().__init__()
        
    def create_web_service(self):
        """ Creates a new ESM shakemap web service client. """
        self.ws_client = ESMShakeMapWebService(
            agency=self.agency, base_url=self.base_url, 
            end_point=self.end_point, version=self.version)

        # Also return the client for further use in case
        # the method is called directly.
        return self.ws_client
    
    def query(self, **kwargs):
        """ Query the web service. """
        return self.ws_client.query(**kwargs)
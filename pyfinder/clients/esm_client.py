# -*-coding: utf-8 -*-
from .services import ESMShakeMapWebService

class ESMShakeMapClient(object):
    """ 
    This class encapsulates the actual ESM shakemap web service 
    client and respective data structure(s). The purpose of this 
    class is to provide a single interface to the ESM web services. 
    The client classes are defined in the clients/services directory.
    """
    def __init__(self):
        self.ws_client = ESMShakeMapWebService()
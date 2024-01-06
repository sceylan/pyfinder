# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

from abc import abstractmethod
from baseclient import BaseWebServiceClient


class ESMShakeMapWSClient(BaseWebServiceClient):
    """
    Class for ESM Shakemap web service client.

    As in the of each client, the class needs to override the following
    abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    """
    def __init__(self, agency=None, base_url=None, end_point=None, version="1"):
        super().__init__(agency, base_url, end_point, version)

    @abstractmethod
    def parse_response(self, file_like_obj):
        """ Parse the data returned by the web service. """
        pass

    @abstractmethod
    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service.
        """
        return ['eventid', 'catalog', 'format', 'flag', 'encoding']



    
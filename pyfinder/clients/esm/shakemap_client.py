# -*- coding: utf-8 -*-
import os
import sys
from abc import abstractmethod

module_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(module_path)
sys.path.append(parent_dir)

from ..baseclient import BaseWebServiceClient


class ESMShakeMapWSClient(BaseWebServiceClient):
    """
    Class for ESM Shakemap web service client.

    As in the of each client, the class needs to override the following
    abstract methods:
    - parse_response(self, file_like_obj)
    - get_supported_options(self)
    """
    def __init__(self, agency="EMSC", base_url="https://esm-db.eu/esmws/", 
                 end_point="shakemap", version="1"):
        super().__init__(agency, base_url, end_point, version)

    def parse_response(self, file_like_obj):
        """ Parse the data returned by the web service. """
        pass

    def get_supported_options(self):
        """ 
        Return the list of options available at the ESM shakemap 
        web service.
        """
        return ['eventid', 'catalog', 'format', 'flag', 'encoding']



    
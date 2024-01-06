# -*- coding: utf-8 -*- 
import sys
import datetime

sys.path.append("..")
from basedatastructure import BaseDataStructure

class ESMShakeMapWSStationNode(BaseDataStructure):
    """
    Pesudo-class for a station-level data in the ESM ShakeMap 
    data structure.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)

    def get_components(self):
        """ 
        Return the list of components, i.e. channels. Each item in 
        the list is a again dictionary.
        """
        return self.get('components')

class ESMShakeMapWSComponentNode(BaseDataStructure):
    """ 
    Pesudo-class for a component-level data in the ESM ShakeMap
    data structure.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)


class ESMShakeMapWSData(BaseDataStructure):
    """
    Main data structure for the ESM ShakeMap web service.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)
        
    def get_creation_time(self):
        """ Return the creation time of the data."""
        return self.get('created')

    def get_stations(self):
        """ 
        Return the list of stations. Each item in the list is a
        dictionary.
        """
        return self.get('stations')

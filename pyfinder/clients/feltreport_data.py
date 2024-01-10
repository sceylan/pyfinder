# -*- coding: utf-8 -*- 
from .basedatastructure import BaseDataStructure

class FeltReportItensityData(BaseDataStructure):
    """ Data structure for fel report intensities. """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)


class FeltReportEventData(BaseDataStructure):
    """ Data structure for felt report event information .
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)
        

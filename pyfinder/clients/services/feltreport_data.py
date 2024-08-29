# -*- coding: utf-8 -*- 
from .basedatastructure import BaseDataStructure

class FeltReportItensityData(BaseDataStructure):
    """ Data structure for feltreport intensities """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)

    def get_event_id(self):
        """ Return the event id. """
        return self._get('unid')
    
    def get_intensities(self):
        """ Return the intensities. """
        return self._get('intensities')
    
    def get_comments(self):
        """ Return the comments. """
        return self._get('comments')
    

class FeltReportEventData(BaseDataStructure):
    """ Data structure for feltreport event information"""
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)
        
    def get_event_deltatime(self):
        """ Return the event delta time. """
        return self._get('ev_deltatime')
    
    def get_longitude(self):
        """ Return the event longitude. """
        return self._get('ev_longitude')
    
    def get_latitude(self):
        """ Return the event latitude. """
        return self._get('ev_latitude')
    
    def get_event_time(self):
        """ Return the event time. """
        return self._get('ev_event_time')
    
    def get_magnitude(self):
        """ Return the event magnitude value. """
        return self._get('ev_mag_value')
    
    def get_magnitude_type(self):
        """ Return the event magnitude type. """
        return self._get('ev_mag_type')
    
    def get_depth(self):
        """ Return the event depth. """
        return self._get('ev_depth')
    
    def get_event_region(self):
        """ Return the event region. """
        return self._get('ev_region')
    
    def get_event_last_update(self):
        """ Return the event last update. """
        return self._get('ev_last_update')
    
    def get_event_nbtestimonies(self):
        """ Return the event number of testimonies. """
        return self._get('ev_nbtestimonies')
    
    def get_event_unid(self):
        """ Return the event unid. """
        return self._get('ev_unid')
    
    def get_event_evid(self):
        """ Return the event evid. """
        return self._get('ev_evid') 
    
    def get_event_id(self):
        """ Return the event id. """
        return self._get('ev_id')
    
    def get_full_count(self):
        """ Return the full count. """
        return self._get('full_count')
    
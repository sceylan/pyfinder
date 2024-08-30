# -*- coding: utf-8 -*- 
from .basedatastructure import BaseDataStructure

class ShakeMapComponentNode(BaseDataStructure):
    """ 
    Component-level data in the ESM/RRSM shakemap web service.
    This level includes channel info and amplitudes. The class
    is a part of the ShakeMapStationAmplitudes data structure.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)

    def get_component_name(self):
        """ Return the channel name. """
        return self._get('name')
    
    def get_component_depth(self):
        """ Return the depth. """
        return self._get('depth')
    
    def get_acceleration(self):
        """ Return the acceleration. """
        return self._get('acc')
    
    def get_acceleration_flag(self):
        """ Return the acceleration flag. """
        return self._get('accflag')
    
    def get_velocity(self):
        """ Return the velocity. """
        return self._get('vel')
    
    def get_velocity_flag(self):
        """ Return the velocity flag. """
        return self._get('velflag')
    
    def get_psa03(self):
        """ Return the PSA03. """
        return self._get('psa03')
    
    def get_psa03_flag(self):
        """ Return the PSA03 flag. """
        return self._get('psa03flag')
    
    def get_psa10(self):
        """ Return the PSA10. """
        return self._get('psa10')
    
    def get_psa10_flag(self):
        """ Return the PSA10 flag. """
        return self._get('psa10flag')
    
    def get_psa30(self):
        """ Return the PSA30. """
        return self._get('psa30')
    
    def get_psa30_flag(self):
        """ Return the PSA30 flag. """
        return self._get('psa30flag')


class ShakeMapStationNode(BaseDataStructure):
    """
    Station-level data for the ESM/RRSM shakemap output.
    This level includes station info and a list for components.
    This class is a part of the ShakeMapStationAmplitudes 
    data structure.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)

    def get_components(self):
        """ 
        Return a List instance of components, i.e. channels. Each item 
        in the list is a again dictionary.
        """
        return self._get('components')

    def get_station_id(self):
        """ Return the station id, which is {netid}.{station code} """
        return self._get('id')
    
    def get_network_code(self):
        """ Return the network id/code. """
        return self._get('netid')
    
    def get_station_code(self):
        """ Return the network code. """
        return self._get('code')
    
    def get_station_name(self):
        """ Return the station name. This is usually the same
        as the station code but may vary depending on the network."""
        return self._get('name')
    
    def get_latitude(self):
        """ Return the station latitude. """
        return self._get('lat')
    
    def get_longitude(self):
        """ Return the station longitude. """
        return self._get('lon')
    
    def get_installation_type(self):
        """ Return the installation type. """
        return self._get('insttype')
    
class ShakeMapStationAmplitudes(BaseDataStructure):
    """
    Station amplitudes data structure for the ESM/RRSM shakemap web service.
    This data structure encapsulates the data returned by the web service
    when format='event_dat'.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)

    def get_creation_time(self):
        """ Return the creation time of the data."""
        return self._get('created')
    
    def get_stations(self):
        """ Return the list of stations. Each item in 
        the list is a dictionary. """
        return self._get('stations')

    def get_station_codes(self):
        """ Return the list of station codes. Each item in 
        the list is a string. """
        return [_sta.get_station_code() for _sta in self.get_stations()]
    
class ShakeMapEventData(BaseDataStructure):
    """
    Event data structure for the ESM/RRSM shakemap web service.
    Encapsulates the data returned by the web service to avoid
    dealing with the dictionary and its keys directly. 

    The get_*() methods exist for both format=event and format=event_dat.
    Therefore, the main client classes handle what should be returned
    based on the format (data set returned by the web service).
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict=data_dict, kwargs=kwargs)
        
    def get_creation_time(self):
        """ Return the creation time of the data."""
        return self._get('created')
    
    def get_event_id(self):
        """ Return the event id. """
        return self._get('id')
    
    def get_catalog(self):
        """ Return the catalog. """
        return self._get('catalog')
    
    def get_latitude(self):
        """ Return the event latitude. """
        return self._get('lat')
    
    def get_longitude(self):
        """ Return the event longitude. """
        return self._get('lon')
    
    def get_magnitude(self):
        """ Return the event magnitude. """
        return self._get('mag')
    
    def get_depth(self):
        """ Return the event depth. """
        return self._get('depth')
    
    def get_origin_time(self):
        """ Return the origin time. """
        return self._get('time') 
    
    def get_time_zone(self):
        """ Return the time zone. """
        return self._get('timezone')
    
    def get_network_code(self):
        """ Return the network id/code. """
        return self._get('netid')
    
    def get_network_desc(self):
        """ Return the network description. """
        return self._get('network')
    
    def get_loc_string(self):
        """ Return the location string. """
        return self._get('locstring')
        
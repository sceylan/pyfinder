# -*- coding: utf-8 -*- 
from .basedatastructure import BaseDataStructure

class PeakMotionChannelData(BaseDataStructure):
    """ Encapsulates the channel data for calling members with dot."""
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict, **kwargs)

    def get_channel_code(self):
        return self._get('channel-code')
    
    def get_acceleration(self):
        """ 
        Return the channel acceleration value.
        Same as get_channel_pga()
        """
        return self._get('pga-value')
    
    def get_channel_pga(self):
        """ 
        Return the channel PGA value.
        Same as get_acceleration()
        """
        return self._get('pga-value')
    
    def get_velocity(self):
        """ 
        Return the channel velocity value.
        Same as get_channel_pgv()
        """
        return self._get('pgv-value')
    
    def get_channel_pgv(self):
        """ 
        Return the channel PGV value.
        Same as get_velocity()
        """
        return self._get('pgv-value')
    
    def get_sensor_azimuth(self):
        return self._get('sensor-azimuth')
    
    def get_sensor_dip(self):
        return self._get('sensor-dip')
    
    def get_sensor_depth(self):
        return self._get('sensor-depth')
    
    def get_low_cut_corner(self):
        return self._get('low-cut-corner')
    
    def get_high_cut_corner(self):
        return self._get('high-cut-corner')
    
class PeakMotionStationData(BaseDataStructure):
    """ Encapsulates the station data for calling members with dot."""
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict, **kwargs)
        self._channels = []

    def add_channel(self, channel_data: PeakMotionChannelData):
        if not isinstance(channel_data, PeakMotionChannelData):
            raise TypeError(
                "Invalid station data type. Expected " +
                "PeakMotionStationData. Got " + str(type(channel_data)))
        
        """ Add a channel data dict to the list of channels."""
        self._channels.append(channel_data)

    def get_channels(self):
        """ Return all the channel data."""
        return self._channels
    
    def get_channel(self, channel_code):
        """ Return the channel data for the given channel code."""
        for _channel in self._channels:
            if _channel.get_channel_code() == channel_code:
                return _channel
            
    def get_channel_codes(self):
        """ Return the channel codes. Channel information is at the second 
         level of the json file. """
        return [channel.get_channel_code() for channel in self.get_channels()]
        
    def get_station_code(self):
        return self._get('station-code')
    
    def get_location_code(self):
        return self._get('location-code')
    
    def get_latitude(self):
        return self._get('station-latitude')
    
    def get_longitude(self):
        return self._get('station-longitude')
    
    def get_elevation(self):
        return self._get('station-elevation')
    
    def get_network_code(self):
        return self._get('network-code')
    
    def get_epicentral_distance(self):
        return self._get('epicentral-distance')
    
class PeakMotionEventData(BaseDataStructure):
    """ Encapsulates the event data for calling members with dot."""
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict, **kwargs)
        
    def get_event_id(self):
        return self._get('event-id')
    
    def get_latitude(self):
        return self._get('event-latitude')
    
    def get_longitude(self):
        return self._get('event-longitude')
    
    def get_depth(self):
        return self._get('event-depth')
    
    def get_event_location_reference(self):
        return self._get('event-location-reference')
    
    def get_event_magnitude_reference(self):
        return self._get('event-magnitude-reference')

    def get_magnitude(self):
        return self._get('event-magnitude')
    
    def get_magnitude_type(self):
        return self._get('magnitude-type')
    
    def get_review_type(self):
        return self._get('review-type')
    
    def get_origin_time(self):
        return self._get('event-time')
    
class PeakMotionData(BaseDataStructure):
    """ 
    Data structure for peak motion data from the RRSM peak-motion
    web service. This service returns a json file with event and 
    amplitude info. Therefore, it is enough to directly assign the 
    internal dict to the json content. This class is provided for
    consistency with other data structures for data interface.

    The json content has the following structure:
    0, 1, 2, ... (station id as incrementing integer)
    |-- event and station information
    |-- sensor channels
        |-- channel id as incrementing integer (0, 1, 2, ...)
            |-- channel information (code, pga, pgv etc)

    The event information is repeated at each station block.
    """
    def __init__(self, data_dict=None, **kwargs):
        super().__init__(data_dict, **kwargs)

        self._event_data: PeakMotionEventData = None
        self._stations: list[PeakMotionStationData] = []

    def add_station(self, station_data: PeakMotionStationData):
        """ Add a station data dict to the list of stations."""
        if not isinstance(station_data, PeakMotionStationData):
            raise TypeError(
                "Invalid station data type. Expected " +
                "PeakMotionStationData. Got " + str(type(station_data)))
        
        self._stations.append(station_data)

    def get_stations(self):
        """ Return all the station data."""
        return self._stations
    
    def get_station(self, station_code):
        """ Return the station data for the given station code."""
        for _station in self._stations:
            if _station.get_station_code() == station_code:
                return _station
            
    def get_station_codes(self):
        """ Return the station codes. Station information is at the first 
         level of the json file. """
        return [station.get_station_code() for station in self.get_stations()]
    
    def get_event_data(self):
        """ Return the event data dict """
        return self._event_data
    
    def set_event_data(self, event_data):
        """ Set the event data dict """
        self._event_data = event_data
 
    

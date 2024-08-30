# -*- coding: utf-8 -*-
import io
import json
from ..baseparser import BaseParser
from ..peakmotion_data import (PeakMotionData, 
                               PeakMotionStationData, 
                               PeakMotionChannelData, 
                               PeakMotionEventData)

class RRSMPeakMotionParser(BaseParser):
    """ Parses the peak motion data from RRSM. The peak motion
    data includes event information as well as the PGA and PGV"""
    def __init__(self):
        super().__init__()

    def validate(self, data):
        """Check the content of the data."""
        return True
    
    def parse(self, data)->PeakMotionData:
        """
        Parse the data. For the peak-motion end point, the data is
        already in json format (a list of jsons). So, this parser 
        just breaks the content into logical components.
        """
        if data and self.validate(data):
            # Store the original content
            self.set_original_content(content=data)

            try:
                json_data = json.load(data)

                if isinstance(json_data, list):
                    json_data = {'event-list': json_data}

            except Exception as e:
                raise ValueError("Invalid data. The content is not " +
                                 "a valid RRSM peak-motion json file. " + str(e))
            
            _data_item = PeakMotionData()

            # Store the whole data at the very top level
            _data_item.set_data(json_data)
            
            # Get the list of events
            event_list = json_data.get('event-list')

            # The first level of the json file contains the event and station
            # information. Construct the event dict from the first node since
            # it is repeated for each station.
            _event_keys = ["event-id", "event-time", "event-magnitude", 
                           "magnitude-type", "event-depth", "event-latitude", 
                           "event-longitude", "review-type",
                           "event-location-reference", "event-magnitude-reference"]
            
            _station_keys = ["network-code", "station-code", "location-code", 
                             "station-latitude", "station-longitude", 
                             "station-elevation", "epicentral-distance", 
                             "review-type"]
            
            _channel_keys = ["channel-code", "pga-value", "pgv-value", 
                                 "sensor-azimuth", "sensor-dip", "sensor-depth", 
                                 "low-cut-corner", "high-cut-corner"]
            
            # Construct the event dict from the first node since it is repeated
            # for each station.
            _event_item = PeakMotionEventData()
            for _key in _event_keys:
                _event_item.set(_key, event_list[0][_key], 
                                add_if_not_exist=True)
                
            _data_item.set_event_data(_event_item)
            
            # Loop through the events and construct the data dicts.
            for event_dict in event_list:
                _station_data = PeakMotionStationData()
                    
                for _key in _station_keys:
                    _station_data.set(_key, event_dict[_key],
                                      add_if_not_exist=True)
                _data_item.add_station(_station_data)
                    
                # Construct the channel data dicts.
                channel_list = event_dict['sensor-channels']
                for channel_dict in channel_list:
                    _channel_data = PeakMotionChannelData()
                            
                    for _key in _channel_keys:
                        _channel_data.set(_key, channel_dict[_key], 
                                          add_if_not_exist=True)
                    _station_data.add_channel(_channel_data)
            
            # Return the main data structure
            return _data_item
        
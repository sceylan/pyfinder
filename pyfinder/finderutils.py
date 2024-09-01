# -*- coding: utf-8 -*-
""" Minimalistic FinDer solution data structure and management classes. """
import logging

class FinderChannelData:
    """ Channel and PGA data structure avaliable from FinDer """
    def __init__(self, latitude=None, longitude=None, network_code=None, 
                 station_code=None, channel_code=None, location_code=None, 
                 pga=None, sncl=None, is_artificial=False):
        self.latitude = latitude
        self.longitude = longitude
        self.network = network_code
        self.station = station_code
        self.channel = channel_code
        self.location = location_code
        self.pga = pga
        self.sncl = sncl
        self.is_artificial = is_artificial

        # Parse the SNCL string to override the individual codes
        if sncl:
            self.set_sncl(sncl)
    
    def get_latitude(self):
        return self.latitude
    
    def set_latitude(self, latitude):
        self.latitude = latitude
    
    def get_longitude(self):
        return self.longitude
    
    def set_longitude(self, longitude):
        self.longitude = longitude
    
    def get_network_code(self):
        return self.network
    
    def set_network_code(self, network_code):
        self.network = network_code
    
    def get_station_code(self):
        return self.station
    
    def set_station_code(self, station_code):
        self.station = station_code
    
    def get_channel_code(self):
        return self.channel
    
    def set_channel_code(self, channel_code):
        self.channel = channel_code
    
    def get_location_code(self):
        return self.location
    
    def set_location_code(self, location_code):
        self.location = location_code
    
    def get_pga(self):
        return self.pga
    
    def set_pga(self, pga):
        self.pga = pga
    
    def get_sncl(self):
        return f"{self.network}.{self.station}.{self.location}.{self.channel}"
    
    def set_sncl(self, sncl):
        """ Set the SNCL string and parse it """
        self.sncl = sncl

        # Parse the SNCL string
        _sncl = sncl.split('.')

        if len(_sncl) != 4:
            logging.error(f"Invalid SNCL string: {sncl}")
            return
        
        self.network = _sncl[0]
        self.station = _sncl[1]
        self.location = _sncl[2]
        self.channel = _sncl[3]

    def is_artificial(self):
        """ Return whether the channel is artificial or not """
        return self.is_artificial
    
    def set_artificial(self, is_artificial):
        """ Mark whether the channel is artificial or not """
        self.is_artificial = is_artificial

    def __str__(self):
        return f"{self.get_latitude()}  {self.get_longitude()}  " + \
            f"{self.get_sncl()}  {self.get_pga()}"
    
    def __repr__(self):
        return f"{self.get_latitude()}  {self.get_longitude()}  " + \
            f"{self.get_sncl()}  {self.get_pga()}"
    

class FinderChannelList(list):
    """ List of FinderChannelData objects """
    def __init__(self, *args):
        super().__init__(*args)
    
    def add_finder_channel(self, latitude, longitude, pga,
                           network_code=None, station_code=None, 
                           channel_code=None, location_code=None,  
                           sncl=None, is_artificial=False):
        """ Add a FinderChannelData object to the list """
        self.append(FinderChannelData(network_code=network_code, 
                                      station_code=station_code, 
                                      channel_code=channel_code, 
                                      location_code=location_code, 
                                      latitude=latitude, 
                                      longitude=longitude, 
                                      pga=pga, sncl=sncl,
                                      is_artificial=is_artificial))
        
    def remove(self, value: FinderChannelData) -> FinderChannelData:
        """ Remove a FinderChannelData object from the list """
        return super().remove(value)
    

class FinderSolution:
    def __init__(self, data_dict=None, **kwargs):
        self._data = data_dict or {}
        self._data.update(kwargs)
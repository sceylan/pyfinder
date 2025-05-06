# -*- coding: utf-8 -*-
""" Minimalistic FinDer solution data structure and management classes. """
from datetime import datetime
import logging

def _to_float(value):
    """ Convert a string to a float value """
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            logging.error(f"Invalid float value: {value}")
            return None
    return value


def read_finder_channels_from_file(file_path: str):
    """
    Parses the FinDer input file `data_0` and returns a FinderChannelList.
    Each line after the first is expected to be formatted as:
    <latitude> <longitude> <SNCL> <trigger_flag> <pga_cmpss>
    """
    channels = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines[1:]:  # skip header
        parts = line.strip().split()
        if len(parts) != 5:
            continue  # skip malformed lines

        try:
            lat = float(parts[0])
            lon = float(parts[1])
            sncl = parts[2]
            flag = int(parts[3])
            pga = float(parts[4])

            net, sta, loc, cha = sncl.strip().split('.')
            channel = FinderChannel(
                network_code=net,
                station_code=sta,
                location_code=loc,
                channel_code=cha,
                latitude=lat,
                longitude=lon,
                pga=pga,
                trigger_flag=flag
            )
            channels.append(channel)
        except Exception as e:
            print(f"Warning: could not parse line: {line.strip()}\nReason: {e}")

    return FinderChannelList(channels)

def read_rupture_polygon_from_file(file_path):
    """ Read the rupture polygon from a file """
    rupture = FinderRupture()

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line_nr, line in enumerate(lines):
            # First line is the number of points
            if line_nr == 0:
                continue

            # Parse the lat, lon, depth values
            lat, lon, depth = line.strip().split()
            rupture.add_point(float(lat), float(lon), float(depth))
    
    return rupture

def read_event_solution_from_file(file_path):
    """ Read the event solution from a file """
    event = FinderEvent()
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # There should be 4 lines in the file
        if len(lines) != 4:
            logging.error(f"Invalid event solution file: {file_path}")
            logging.error(f"Parsing anyway...")
        
        # First line is the origin time in epoch
        event.set_origin_time_epoch(int(lines[0].strip()))

        # Second line is the magnitude
        event.set_magnitude(float(lines[1].strip()))

        # Third line is lat/lon
        lat, lon = lines[2].strip().split()
        event.set_latitude(float(lat.strip()))
        event.set_longitude(float(lon.strip()))

        # Fourth line is the depth (reported as a negative number in the file)
        event.set_depth(abs(float(lines[3].strip())))

    return event

class FinderChannel:
    """ Channel and PGA data structure avaliable from FinDer """
    def __init__(self, latitude=None, longitude=None, network_code=None, 
                 station_code=None, channel_code=None, location_code=None, 
                 pga=None, sncl=None, is_artificial=False, trigger_flag=None):
        self.latitude = latitude
        self.longitude = longitude
        self.network = network_code
        self.station = station_code
        self.channel = channel_code
        self.location = location_code
        self.pga = pga
        self.sncl = sncl
        self.trigger_flag = trigger_flag

        # A channel is aritificial if it is not a real channel
        # but a synthetic one to ensure the FinDer solution is stable.
        self.is_artificial = is_artificial

        if sncl:
            # Parse the SNCL string to override the individual codes
            self.set_sncl(sncl)
    
    def get_latitude(self):
        return self.latitude
    
    def set_latitude(self, latitude):
        """ Set the latitude value even if it is not valid """
        latitude = _to_float(latitude)
        
        if latitude is None:
            logging.error(f"Invalid latitude value is being assigned: {latitude}")

        self.latitude = latitude
    
    def get_longitude(self):
        return self.longitude
    
    def set_longitude(self, longitude):
        """ Set the longitude value even if it is not valid """
        longitude = _to_float(longitude)

        if longitude is None:
            logging.error(f"Invalid longitude value is being assigned: {longitude}")
            
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
        """ Set the PGA value even if it is not valid """
        pga = _to_float(pga)
        
        if pga is None:
            logging.error(f"Invalid PGA value is being assigned: {pga}")

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
        
        # Override all the individual codes
        self.network = _sncl[0].strip()
        self.station = _sncl[1].strip()
        self.location = _sncl[2].strip()
        self.channel = _sncl[3].strip()

    def is_artificial(self):
        """ Return whether the channel is artificial or not """
        return self.is_artificial
    
    def set_artificial(self, is_artificial):
        """ Mark whether the channel is artificial or not """
        self.is_artificial = is_artificial

    def get_trigger_flag(self):
        """ Return the trigger flag """
        return self.trigger_flag
    
    def set_trigger_flag(self, trigger_flag):
        """ Set the trigger flag """
        self.trigger_flag = trigger_flag

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
    
    def add_finder_channel(self, latitude, longitude, pga, network_code=None, 
                           station_code=None, channel_code=None, location_code=None,  
                           sncl=None, is_artificial=False):
        """ 
        Add a FinderChannelData object to the list. This is an optional 
        encapsulation method for convenience. Otherwise, the user can
        directly append an FinderChannel object to the list.
        """
        self.append(
            FinderChannel(network_code=network_code, 
                          station_code=station_code, 
                          channel_code=channel_code, 
                          location_code=location_code, 
                          latitude=latitude, 
                          longitude=longitude, 
                          pga=pga, sncl=sncl,
                          is_artificial=is_artificial))
        
    def remove(self, value: FinderChannel) -> FinderChannel:
        """ Remove a FinderChannelData object from the list """
        return super().remove(value)
    

class FinderEvent:
    """ Basic event information from FinDer solution"""
    def __init__(self, event_id=None, finder_event_id=None, origin_time_epoch=None,
                 latitude=None, longitude=None, depth=None, magnitude=None) -> None:
        # Event ID from the web service
        self.event_id = event_id

        # Origin time. This should be the same as finder_event_id
        self.origin_time_epoch = origin_time_epoch

        # Finder event ID
        self.finder_event_id = finder_event_id
        
        # Event location
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth

        # Event magnitude
        self.magnitude = magnitude

    def get_origin_time_epoch(self, dtype=int):
        if dtype == int:
            return int(self.origin_time_epoch)
        elif dtype == float:
            return float(self.origin_time_epoch)
        elif dtype == str:
            return str(self.origin_time_epoch)
        else:
            return datetime.fromtimestamp(self.origin_time_epoch)

    def set_origin_time_epoch(self, origin_time_epoch):
        """ Set the origin time as epoch time """
        if not isinstance(origin_time_epoch, int):
            origin_time_epoch = int(origin_time_epoch)
        self.origin_time_epoch = origin_time_epoch

    def get_event_id(self):
        """ Return the event ID as used in the web service """
        return self.event_id
    
    def set_event_id(self, event_id):
        """ Set the event ID as used in the web service """
        self.event_id = event_id

    def get_finder_event_id(self):
        """ Return the Finder's internal event ID """
        return self.finder_event_id
    
    def set_finder_event_id(self, event_id):
        """ Set the Finder's internal event ID """
        self.finder_event_id = event_id

    def get_latitude(self):
        """ Return the latitude value """
        if not isinstance(self.latitude, float):
            self.latitude = _to_float(self.latitude)
        return self.latitude
    
    def set_latitude(self, latitude):
        """ Set the latitude value even if it is not valid """
        latitude = _to_float(latitude)
        if latitude is None:
            logging.error(f"Invalid latitude value is being assigned: {latitude}")

        self.latitude = latitude

    def get_longitude(self):
        """ Return the longitude value """
        if not isinstance(self.longitude, float):
            self.longitude = _to_float(self.longitude)
        return self.longitude
    
    def set_longitude(self, longitude):
        """ Set the longitude value even if it is not valid """
        longitude = _to_float(longitude)
        if longitude is None:
            logging.error(f"Invalid longitude value is being assigned: {longitude}")
            
        self.longitude = longitude

    def get_depth(self):
        """ Return the depth value """
        if not isinstance(self.depth, float):
            self.depth = _to_float(self.depth)
        return self.depth
    
    def set_depth(self, depth):
        """ Set the depth value even if it is not valid """
        depth = _to_float(depth)
        if depth is None:
            logging.error(f"Invalid depth value is being assigned: {depth}")
            
        self.depth = depth

    def get_magnitude(self):
        """ Return the magnitude value """
        if not isinstance(self.magnitude, float):
            self.magnitude = _to_float(self.magnitude)
        return self.magnitude
    
    def set_magnitude(self, magnitude):
        """ Set the magnitude value even if it is not valid """
        magnitude = _to_float(magnitude)
        if magnitude is None:
            logging.error(f"Invalid magnitude value is being assigned: {magnitude}")
            
        self.magnitude = magnitude

    def __str__(self):
        _lat = round(self.get_latitude(), 3)
        _lon = round(self.get_longitude(), 3)
        _depth = round(self.get_depth(), 2)
        _mag = round(self.get_magnitude(), 1)

        return f"Lat/Lon {_lat} {_lon}, Depth {_depth} km, Mfd  {_mag}"
    
    def __repr__(self):
        return f"{self.get_latitude()}  {self.get_longitude()}  " + \
            f"{self.get_depth()}  {self.get_magnitude()}"


class FinderRupture:
    """ FinDer rupture polygon solution"""
    def __init__(self):
        self.lats = []
        self.lons = []
        self.depths = []

    def add_point(self, latitude, longitude, depth):
        """ Add a point to the rupture polygon """
        self.lats.append(latitude)
        self.lons.append(longitude)
        self.depths.append(depth)

    def get_points(self) -> list:
        """ Return the rupture polygon points as Lat-Lon-depth tuples """
        return list(zip(self.lats, self.lons, self.depths))
    
    def to_WKT(self) -> str:
        """ Convert the rupture polygon to a WKT string as POLYGON_Z (includes depth) """
        return f"POLYGON Z(({', '.join([f'{lon} {lat} {depth}' for lat, lon, depth in self.get_points()])}))"
    
    def __str__(self):
        return self.to_WKT()
    
    def __repr__(self):
        return f"{self.to_WKT()}"
    

class FinderSolution:
    """ 
    Container and manager class for all FinDer solutions and channel data 
    """
    def __init__(self, event_id=None, finder_event_id: str=None, rupture: FinderRupture=None, 
                 event: FinderEvent=None, channels: FinderChannelList=None):
        self.rupture = rupture
        self.event = event
        self.channels = channels
        self.finder_event_id = finder_event_id
        self.event_id = event_id

    def get_event_id(self) -> str:
        """ Return the true event ID from web services """
        return self.event_id
    
    def set_event_id(self, event_id: str):
        """ Set the true event ID (from web services) for self and 
        also for the event object """
        self.event_id = event_id

        if self.event:
            self.event.set_event_id(event_id)

    def get_finder_event_id(self) -> str:
        """ Return the FinDer's internal event ID """
        return self.finder_event_id
    
    def set_finder_event_id(self, event_id: str):
        """ Set the FinDer's internal event ID for self and 
        also for the event object """
        self.finder_event_id = event_id

        if self.event:
            self.event.set_finder_event_id(event_id)

    def get_rupture(self) -> FinderRupture:
        return self.rupture
    
    def get_event(self) -> FinderEvent:
        return self.event
    
    def get_channels(self) -> FinderChannelList:
        return self.channels
    
    def set_rupture(self, rupture_polygon: FinderRupture):
        self.rupture = rupture_polygon

    def set_event(self, event: FinderEvent):
        self.event = event

    def set_channels(self, channels: FinderChannelList):
        self.channels = channels

    def __str__(self):
        return f"Finder event :: {self.event}\nFinDer rupture :: {self.rupture}"
    
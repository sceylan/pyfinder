# -*-encoding: utf-8-*-
""" Classes for handling and formatting data from the web services 
for the FinDer executable. """

import numpy as np
import datetime
import logging
import fnmatch
from typing import Union
from .calculator import Calculator
from pyfinderconfig import pyfinderconfig
from clients.services.shakemap_data import ShakeMapEventData, ShakeMapStationAmplitudes
from finderutils import FinderChannelList

# Thresholds for the RRSM peak motion data that are used to filter out
# the stations with PGA/PGV values that are not in the range.
RRSM_PEAKMOTION_PGA_MIN = 0.00001
RRSM_PEAKMOTION_PGA_MAX = 4*9.806 # m/s/s
RRSM_PEAKMOTION_PGV_MIN = 0.000001
RRSM_PEAKMOTION_PGV_MAX = 1.0 # m/s
RRSM_PEAKMOTION_PGV_BROADBAND_MIN = 0.000001
RRSM_PEAKMOTION_PGV_BROADBAND_MAX = 0.013 # m/s

def get_epoch_time(time_str):
    """ Convert the time string to epoch time. """
    formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f",
               "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S",]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(time_str, fmt).timestamp()
        except ValueError:
            pass
    
class BaseDataFormatter(object):
    def __init__(self):
        pass

    def format_data(self, event_data, amplitudes) -> Union[str, FinderChannelList]:
        """ Format the data for the FinDer executable. """
        pass


class ESMShakeMapDataFormatter(BaseDataFormatter):
    """ Class for formatting the ESM ShakeMap data for the FinDer executable. """
    def __init__(self):
        pass

    def format_data(self, event_data: ShakeMapEventData, 
                    amplitudes: ShakeMapStationAmplitudes) -> Union[str, FinderChannelList]:
        """ Format the data for the FinDer executable. """
        logging.info(f"Formatting the ESM ShakeMap: {type(amplitudes)}.......")
        is_live_mode = pyfinderconfig["finder-executable"]["finder-live-mode"]

        time_epoch = int(get_epoch_time(event_data.get_origin_time()))

        # Print the event information
        logging.info(f"Event ID: {event_data.get_event_id()}")
        logging.info(f"|- Time: {event_data.get_origin_time()}")
        logging.info(f"|- Latitude: {event_data.get_latitude()}")
        logging.info(f"|- Longitude: {event_data.get_longitude()}")
        logging.info(f"|- Depth: {event_data.get_depth()}")
        logging.info(f"|- Magnitude: {event_data.get_magnitude()}")

        # Collect the station, channel and PGA information
        stations = amplitudes.get_stations()
        logging.info(f"There are {len(stations)} stations. Looking for the maximum PGA for each.")
        
        selected_channels = []
        pga_strings = []
        
        # Create a FinderChannelList object to store the channel data
        finder_channels = FinderChannelList()

        for station in stations:
            # Find the component with the maximum PGA
            pga = -np.inf
            selected_channel = None

            for channel in station.get_components():
                if channel.get_acceleration() > pga:
                    pga = channel.get_acceleration()
                    selected_channel = channel

            if selected_channel is not None:
                selected_channels.append(selected_channel)

                latitude = station.get_latitude()
                longitude = station.get_longitude()
                network_code = station.get_network_code()
                station_code = station.get_station_code()
                channel_code = selected_channel.get_component_name()

                # Remove any leading dots from all codes
                network_code = network_code.lstrip(".")
                station_code = station_code.lstrip(".")
                channel_code = channel_code.lstrip(".")
                location_code = ""    

                if len(channel_code.split(".")) > 1:
                    location_code, channel_code = channel_code.split(".")

                # Create the SNCL code
                sncl = f"{network_code}.{station_code}.{location_code}.{channel_code}"

                # Convert the percent PGA to cm/s/s
                pga = Calculator.percent_g_to_cm_s2(pga)

                if is_live_mode == False:
                    pga = np.log10(pga)

                if is_live_mode:
                    pga_strings.append(f"{latitude} {longitude} {sncl} {time_epoch} {round(pga, 3)}")

                    logging.ok(f"{sncl} PGA: {round(pga, 3)} m/s/s at " + \
                               f" Latitude: {latitude}, Longitude: {longitude}")
                    
                else:
                    pga_strings.append(f"{latitude} {longitude} {round(pga, 3)}")

                    logging.ok(f"{sncl} logPGA: {round(pga, 3)} m/s/s at " + \
                               f" Latitude: {latitude}, Longitude: {longitude}")
                    
                finder_channels.add_finder_channel(latitude=latitude, longitude=longitude,
                                                   pga=pga, sncl=sncl, is_artificial=False)

        # Create an artificial maximum PGA at the epicenter to make FinDer 
        # stick to the actual location. 
        fake_latitude = event_data.get_latitude()
        fake_longitude = event_data.get_longitude()
        fake_station = f"XX.NONE.00.HNZ"

        # Magnitude-dependent artificial PGA 
        magnitude = event_data.get_magnitude()
        depth = event_data.get_depth() or 10

        # Find the maximum observed PGA
        max_oberserved_pga = np.max([channel.get_acceleration() for channel in selected_channels])
        logging.info(f"Maximum observed PGA: {round(max_oberserved_pga, 3)} cm/s/s at the stations.")
        fake_max_pga = np.max([Calculator.predict_PGA_from_magnitude(
                magnitude=magnitude, event_depth=depth, log_scale=(is_live_mode == False)), 
                max_oberserved_pga * 1.2]) 
        logging.info(f"Use log10(PGA) in the FinDer input: {is_live_mode == False}")
        logging.info(f"Artificial maximum PGA: {round(fake_max_pga, 3)} cm/s/s at the epicenter.")
        
        # List to store merged the coordinates and PGAs 
        data = []
        
        # Origin time epoch goes first as the header. The header is
        # timestamp and time step increment, which is zero in our case.
        data.append(f"# {time_epoch} 0")

        # Append the epicenter
        if is_live_mode:
            data.append(f"{fake_latitude} {fake_longitude} {fake_station} {time_epoch} {round(fake_max_pga, 3)}")
        else:
            data.append(f"{fake_latitude} {fake_longitude} {np.round(fake_max_pga, 3)}")

        finder_channels.add_finder_channel(latitude=fake_latitude, longitude=fake_longitude,
                                           pga=fake_max_pga, sncl=fake_station, is_artificial=True)

        # Append the stations
        for pga_string in pga_strings:
            data.append(pga_string)

        return "\n".join(data).encode("ascii"), finder_channels
    

        
class RRSMPeakMotionDataFormatter(BaseDataFormatter):
    """ Class for formatting the RRSM peak motion data for the FinDer executable. """
    def __init__(self):
        pass

    def format_data(self, event_data, amplitudes) -> Union[str, FinderChannelList]:
        """ Format the data for the FinDer executable. """
        logging.info("Formatting the RRSM PeakMotionData.......")
        
        station_codes = event_data.get_station_codes()

        # Swap variables
        peak_motions = event_data
        event_data = peak_motions.get_event_data()
        is_live_mode = pyfinderconfig["finder-executable"]["finder-live-mode"]
        
        # Print the event information
        logging.info(f"Event ID: {event_data.get_event_id()}")
        logging.info(f"|- Time: {event_data.get_origin_time()}")
        logging.info(f"|- Latitude: {event_data.get_latitude()}")
        logging.info(f"|- Longitude: {event_data.get_longitude()}")
        logging.info(f"|- Depth: {event_data.get_depth()}")
        logging.info(f"|- Magnitude: {event_data.get_magnitude()}, {event_data.get_magnitude_type()}")

        # Collect the station, channel and PGA information
        logging.info(f"There are {len(station_codes)} stations. Looking for the maximum PGA for each.")
        all_stations = []
        all_pga = []

        # Create a FinderChannelList object to store the channel data passed to the FinDer
        finder_channels = FinderChannelList()

        for station_code in station_codes:
            station_data = peak_motions.get_station(station_code=station_code)
            all_stations.append(station_data)

            # Find the component with the maximum PGA
            pga = -np.inf
            selected_channel = None

            for channel in station_data.get_channels():
                if channel.get_channel_pga() > pga:
                    pga = channel.get_channel_pga()
                    selected_channel = channel
            all_pga.append(pga)

        # Sort the stations by the maximum PGA just for logging in order
        sorted_stations = [station for _, station in sorted(zip(all_pga, all_stations), reverse=True)]

        # Valid stations have PGAs within the range. Invalid stations are either
        # missing the PGA value or the value is not in the range.
        valid_stations = []
        valid_pgas = []
        valid_channels = []
        invalid_stations = []

        for station_data in sorted_stations:
            latitude = station_data.get_latitude()
            longitude = station_data.get_longitude()
            network_code = station_data.get_network_code()
            station_code = station_data.get_station_code()
            distance = station_data.get_epicentral_distance()

            # Find the component with the maximum PGA
            pga = -np.inf
            selected_channel = None

            for channel in station_data.get_channels():
                # A PGA should be within the range to be considered.
                channel_pga = np.abs(channel.get_channel_pga())
                
                if channel_pga > pga and \
                    channel_pga >= RRSM_PEAKMOTION_PGA_MIN \
                        and channel_pga <= RRSM_PEAKMOTION_PGA_MAX:

                    pga = channel_pga
                    selected_channel = channel

            if selected_channel is None:
                # No valid PGA found for this station. Either PGAs for all componentds are 
                # not in the range, or value is missing.
                invalid_stations.append(station_data)
                logging.warning(f"Discarding station {station_code}. No (valid) PGA found.")
                
            elif pga <= RRSM_PEAKMOTION_PGA_MIN or pga >= RRSM_PEAKMOTION_PGA_MAX:
                # The maximum PGA for this station is not in the range.
                invalid_stations.append(station_data)
                logging.warning(f"Discarding station {network_code}.{station_code}. PGA ({pga}) not in the range.")
            
            else:
                # A valid PGA found for this station.
                valid_stations.append(station_data)

                # Log10 transform the PGA if NOT in the live mode. Otherwise, 
                # keep it in cm/s/s as it is.
                if is_live_mode == False:
                    pga = np.log10(pga)
                valid_pgas.append(pga)

                # Remove any leading dots from all codes
                network_code = network_code.lstrip(".")
                station_code = station_code.lstrip(".")
                channel_code = selected_channel.get_channel_code().lstrip(".")

                # Check if the channel code has a location code
                location_code = ""
                if len(channel_code.split(".")) > 1:
                    location_code, channel_code = channel_code.split(".")
            
                sncl = f"{network_code}.{station_code}.{location_code}.{channel_code}"
                valid_channels.append(sncl)

                finder_channels.add_finder_channel(latitude=latitude, longitude=longitude,
                                                   pga=pga, sncl=sncl, is_artificial=False)

                if is_live_mode:
                    logging.ok(f"{sncl}, PGA: {round(pga, 3)} cm/s/s at {round(distance, 2)} km,"
                               f" Latitude: {latitude}, Longitude: {longitude}")
                else:
                    logging.ok(f"{sncl}, log10(PGA): {round(pga, 3)} cm/s/s at {round(distance, 2)} km,"
                            f" Latitude: {latitude}, Longitude: {longitude}")
            
        # A small summary
        logging.info(f"Total number of stations: {len(sorted_stations)}")
        logging.info(f"Number of valid stations: {len(valid_stations)} out of {len(sorted_stations)}")
        logging.info(f"Number of invalid stations: {len(invalid_stations)} out of {len(sorted_stations)}")

        # We insert a fake maximum PGA at the epicenter to make FinDer 
        # stick to the actual location. This fake PGA is 1% more than the
        # maximum PGA of the stations. 
        fake_latitude = event_data.get_latitude()
        fake_longitude = event_data.get_longitude()
        fake_station = f"XX.NONE.00.HNZ"
        
        # Magnitude-dependent artificial PGA 
        magnitude = event_data.get_magnitude()
        depth = event_data.get_depth() or 10

        # Find the maximum observed PGA
        max_oberserved_pga = np.max(valid_pgas)
        logging.info(f"Maximum observed PGA: {round(max_oberserved_pga, 3)} cm/s/s at the stations.")
        fake_max_pga = np.max([Calculator.predict_PGA_from_magnitude(
                magnitude=magnitude, event_depth=depth, log_scale=(is_live_mode == False)), 
                max_oberserved_pga * 1.2]) 
        logging.info(f"Use log10(PGA) in the FinDer input: {is_live_mode == False}")
        logging.info(f"Artificial maximum PGA: {round(fake_max_pga, 3)} cm/s/s at the epicenter.")
        
        # Merge the coordinates and PGAs into a string
        data = []

        # Origin time epoch goes first as the header. The header is 
        # timestamp and time step increment, which is zero in our case.
        time_epoch = int(get_epoch_time(event_data.get_origin_time()))
        data.append(f"# {time_epoch} 0")

        # Append the epicenter
        if is_live_mode:
            data.append(f"{fake_latitude} {fake_longitude} {fake_station} {time_epoch} {fake_max_pga}")
        else:
            data.append(f"{fake_latitude} {fake_longitude} {np.round(fake_max_pga, 3)}")

        finder_channels.add_finder_channel(latitude=fake_latitude, longitude=fake_longitude,
                                           pga=fake_max_pga, sncl=fake_station, is_artificial=True)

        # Sort all arrays by the PGA values
        valid_stations = [station for _, station in sorted(zip(valid_pgas, valid_stations), reverse=True)]
        valid_channels = [channel for _, channel in sorted(zip(valid_pgas, valid_channels), reverse=True)]
        valid_pgas = sorted(valid_pgas, reverse=True)

        # Append the stations
        for station_data, pga, sncl_data in zip(valid_stations, valid_pgas, valid_channels):
            latitude = station_data.get_latitude()
            longitude = station_data.get_longitude()
            
            if is_live_mode:
                data.append(f"{latitude}  {longitude}  {sncl_data}  {time_epoch}  {np.round(pga, 3)}")
            else:
                data.append(f"{latitude} {longitude} {np.round(pga, 3)}")
            
        # Return the formatted data
        return "\n".join(data).encode("ascii"), finder_channels
    
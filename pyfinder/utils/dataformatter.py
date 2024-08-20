# -*-encoding: utf-8-*-
""" Classes for handling and formatting data from the web services 
for the FinDer executable. """

import numpy as np
import datetime
from .calculator import Calculator
import logging

# Thresholds for the RRSM peak motion data that are used to filter out
# the stations with PGA/PGV values that are not in the range.
RRSM_PEAKMOTION_PGA_MIN = 0.00001
RRSM_PEAKMOTION_PGA_MAX = 8*9.806 # m/s/s
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
    
class DataFormatter(object):
    def __init__(self):
        pass

    def format_data(self, data_object):
        """ Format the data for the FinDer executable. """
        pass

class PeakMotionDataFormatter(DataFormatter):
    def __init__(self):
        pass

    def format_data(self, data_object):
        """ Format the data for the FinDer executable. """
        logging.info("Formatting the PeakMotionData.......")

        station_codes = data_object.get_station_codes()
        event_data = data_object.get_event_data()

        # Print the event information
        logging.info(f"Event ID: {event_data.get_event_id()}")
        logging.info(f"|- Date: {event_data.get_origin_time()}")
        logging.info(f"|- Latitude: {event_data.get_event_latitude()}")
        logging.info(f"|- Longitude: {event_data.get_event_longitude()}")
        logging.info(f"|- Depth: {event_data.get_event_depth()}")

        # Collect the station, channel and PGA information
        logging.info(f"There are {len(station_codes)} stations. Looking for the maximum PGA for each.")
        all_stations = []
        all_pga = []
        for station_code in station_codes:
            station_data = data_object.get_station(station_code)
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
            latitude = station_data.get_station_latitude()
            longitude = station_data.get_station_longitude()
            network_code = station_data.get_network_code()
            station_code = station_data.get_station_code()
            distance = station_data.get_epicentral_distance()

            # Find the component with the maximum PGA
            pga = -np.inf
            selected_channel = None

            for channel in station_data.get_channels():
                # A PGA should be within the range to be considered.
                if channel.get_channel_pga() > pga and \
                    channel.get_channel_pga() >= RRSM_PEAKMOTION_PGA_MIN \
                    and channel.get_channel_pga() <= RRSM_PEAKMOTION_PGA_MAX:

                    pga = channel.get_channel_pga()
                    selected_channel = channel

            if selected_channel is None:
                # No valid PGA found for this station. Either PGAs for all componentds are 
                # not in the range, or value is missing.
                invalid_stations.append(station_data)
                logging.warning(f"Discarding station {station_code}. No (valid) PGA found.")
                
            elif pga <= RRSM_PEAKMOTION_PGA_MIN or pga >= RRSM_PEAKMOTION_PGA_MAX:
                # The maximum PGA for this station is not in the range.
                invalid_stations.append(station_data)
                logging.warning(f"Discarding station {network_code}.{station_code} (blacklisted). PGA ({pga}) not in the range.")
            
            else:
                # A valid PGA found for this station.
                valid_stations.append(station_data)
                valid_pgas.append(pga)
                sncl = f"{network_code}.{station_code}.{selected_channel.get_channel_code()}"
                valid_channels.append(sncl)

                logging.ok(f"{sncl}, PGA: {round(pga, 3)} cm/s/s at {round(distance, 2)} km, Latitude: {latitude}, Longitude: {longitude}")
        
        # A small summary
        logging.info(f"Total number of stations: {len(sorted_stations)}")
        logging.info(f"Number of valid stations: {len(valid_stations)} out of {len(sorted_stations)}")
        logging.info(f"Number of invalid stations: {len(invalid_stations)} out of {len(sorted_stations)}")

        # We insert a fake maximum PGA at the epicenter to make FinDer 
        # stick to the actual location. This fake PGA is 1% more than the
        # maximum PGA of the stations. 
        fake_max_pga = np.max(valid_pgas) * 1.01
        fake_latitude = event_data.get_event_latitude()
        fake_longitude = event_data.get_event_longitude()
        fake_station = f"XE.EPIC.HNZ"
        logging.info(f"Artificial maximum PGA: {round(fake_max_pga, 3)} cm/s/s at the epicenter.")

        # Merge the coordinates and PGAs into a string
        data = []

        # Origin time epoch goes first as the header. The header is 
        # timestamp and time step increment, which is zero in our case.
        data.append(f"{int(get_epoch_time(event_data.get_origin_time()))} 0")

        # Append the epicenter
        data.append(f"{fake_latitude} {fake_longitude} {fake_station} {fake_max_pga} ")

        # Append the stations
        for station_data, pga, sncl_data in zip(valid_stations, valid_pgas, valid_channels):
            latitude = station_data.get_station_latitude()
            longitude = station_data.get_station_longitude()
            
            data.append(f"{latitude} {longitude} {sncl_data} {pga}")

        # Return the formatted data
        return "\n".join(data)
    
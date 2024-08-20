# *-* coding: utf-8 -*-
from clients import PeakMotionData

try:
    from seiscomp.datamodel import Origin
    USE_SEISCOMP = True
except ImportError:
    USE_SEISCOMP = False

try:
    # Import the libFinder bindings library
    import pylibfinder
    from pylibfinder import FiniteFault 
    from pylibfinder.FiniteFault import (Coordinate, Coordinate_List)
except ImportError:
    raise ImportError("Could not import pylibfinder. Are the binginds compiled?")

class FinderLibrary(object):
    """ Wrapper class for managing the FinDer library"""
    def __init__(self):
        pass

    def execute(self, data_object):
        """ Call the FinDer library methods for the data passed in"""
        raise NotImplementedError("FinderLibrary.execute() method is not implemented yet")

        # # Coordinate list
        # _coordinate_list = FiniteFault.Coordinate_List()
        
        # for _station in data_object.get_stations():
        #     longitude = _station.get_station_longitude()
        #     latitude = _station.get_station_latitude()
        #     _coordinate_list.push_back(FiniteFault.Coordinate(lon=longitude, lat=latitude))

        # # Initialize the FinDer library
        # FiniteFault.Finder.Init("/usr/local/src/FinDer/config/finder.config", FiniteFault.Coordinate_List())

        # event_data = data_object.get_event_data()
        # epicenter = Coordinate(lon=event_data.get_event_longitude(), 
        #                        lat=event_data.get_event_latitude())
        # event_id = event_data.get_event_id()
        # print("Epicenter: ", event_id, epicenter.get_lon(), epicenter.get_lat())

        # amplitude_data = data_object.get_amplitude_data()
        # print("Amplitude data: ", amplitude_data.get_station_code())
        
        # # _finder = libfinder.Finder("/usr/local/src/FinDer/config/finder.config", [])
        # # if isinstance(data_object, PeakMotionData):
        # #     # Call the FinDer library
        # #     libfinder.FinDer(data_object)

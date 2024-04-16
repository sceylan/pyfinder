# *-* coding: utf-8 -*-
from clients import PeakMotionData
try:
    # Import the libFinder bindings library
    import pylibfinder
    from pylibfinder import FiniteFault as libfinder
except ImportError:
    raise ImportError("Could not import pylibfinder. Are the binginds compiled?")



class FinderLibrary(object):
    """ Wrapper class for managing the FinDer library"""
    def __init__(self):
        pass

    def execute(self, data_object):
        """ Call the FinDer library methods for the data passed in"""
        print(dir(pylibfinder))

        print(dir(libfinder))
        _finder = libfinder.Finder("/usr/local/src/FinDer/config/finder.config", [])
        # if isinstance(data_object, PeakMotionData):
        #     # Call the FinDer library
        #     libfinder.FinDer(data_object)

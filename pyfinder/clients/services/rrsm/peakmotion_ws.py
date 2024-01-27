# -*- coding: utf-8 -*-
from .shakemap_ws import RRSMShakeMapWebService
from .peakmotion_parser import RRSMPeakMotionParser

class RRSMPeakMotionWebService(RRSMShakeMapWebService):
    """ 
    This class is web service client for the RRSM peak motion web service.
    The RRSM peak motion web service complementary to the RRSM shakemap web
    service, but also includes the event information in addition to the PGA
    and PGV values. Spectral amplitudes are not included. The end point is
    'peak-motion'.
    """
    def __init__(self, agency="ORFEUS", base_url="http://orfeus-eu.org/odcws/rrsm/", 
                 end_point="peak-motion", version="1"):
        super().__init__(agency, base_url, end_point, version)

    def parse_response(self, file_like_obj=None, options=None):
        """ Parse the data returned by the web service. """
        if file_like_obj:
            parser = RRSMPeakMotionParser()

            data = parser.parse(file_like_obj)
            
            self.set_data(data)

        return self.get_data()
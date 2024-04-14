# -*- coding: utf-8 -*-
""" 
Client modules that consume the web services of the data centers 
with their data structures.
"""
from .basewebservice import BaseWebService
from .esm.shakemap_ws import ESMShakeMapWebService
from .rrsm.shakemap_ws import RRSMShakeMapWebService
from .rrsm.peakmotion_ws import RRSMPeakMotionWebService
from .emsc.feltreport_ws import EMSCFeltReportWebService, MissingRequiredFieldError
from .basewebservice import InvalidQueryOption, InvalidOptionValue

# Data structures
from .peakmotion_data import PeakMotionData, PeakMotionStationData, PeakMotionChannelData
from .shakemap_data import ShakeMapEventData, ShakeMapComponentNode, ShakeMapStationAmplitudes, ShakeMapStationNode
from .feltreport_data import FeltReportEventData, FeltReportItensityData
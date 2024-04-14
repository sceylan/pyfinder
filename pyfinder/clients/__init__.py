# -*-coding: utf-8 -*-
""" Manager classes for the web service clients. """
from .esm_client import ESMShakeMapClient
from .rrsm_client import RRSMShakeMapClient
from .rrsm_client import RRSMPeakMotionClient
from .emsc_client import EMSCFeltReportClient

# Data structures from the services module for ease of import
from .services import (PeakMotionData, ShakeMapEventData, FeltReportEventData, 
                       FeltReportItensityData, PeakMotionStationData, 
                       PeakMotionChannelData, ShakeMapComponentNode, 
                       ShakeMapStationAmplitudes, ShakeMapStationNode)

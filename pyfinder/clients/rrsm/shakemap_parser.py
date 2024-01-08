# -*- coding: utf-8 -*-
from ..esm.shakemap_parser import ESMShakeMapParser

class RRSMShakeMapParser(ESMShakeMapParser):
    """ 
    RRSM output is the same as ESM (with format=event_dat); 
    therefore, the parser is the same.
    """
    pass


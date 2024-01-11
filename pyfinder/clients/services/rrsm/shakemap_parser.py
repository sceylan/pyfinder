# -*- coding: utf-8 -*-
from ..esm.shakemap_parser import ESMShakeMapParser

class RRSMShakeMapParser(ESMShakeMapParser):
    """ 
    RRSM output is the same as ESM (with format=event_dat); 
    therefore, the parser is the same.
    """
    def __init__(self):
        super().__init__()

   
    def validate(self, data):
        """Check the content of the data."""
        return True

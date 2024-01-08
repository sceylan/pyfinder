# -*- coding: utf-8 -*-
import datetime
import xmltodict
from ..baseparser import BaseParser
from .shakemap_data import ESMShakeMapData
from .shakemap_data import ESMShakeMapStationNode
from .shakemap_data import ESMShakeMapComponentNode

class ESMShakeMapParser(BaseParser):
    """
    Parser class for the ESM ShakeMap web service output.
    The return from the web service is an XML file without
    and style sheet. The parser converts the XML file to
    a dictionary, and then creates a data structure.
    """
    def __init__(self):
        super().__init__()

    def _parse(self, data):
        """
        Parse the data returned by the ESM ShakeMap web service.
        This method converts the XML content to a dictionary only
        for format="event_dat". 
        """
        self.set_original_content(content=data)

        # Convert the XML content to a dictionary. This is easier
        # to work with.
        xml_content = xmltodict.parse(data)

        # Initialize the main data structure for the ESM ShakeMap.
        # The top-level data structure is a dictionary with two keys:
        # - created: The creation time of the data.
        # - stations: A list of stations.
        _esm_toplevel_data = {
            "created": datetime.datetime.fromtimestamp(
                int(xml_content['stationlist']['@created'])),
            "stations": []}
        esm_shakemap_data = ESMShakeMapData(_esm_toplevel_data)

        for _sta in xml_content['stationlist']['station']:
            # Station ID is constructed using network and station code 
            # to search for the station in station list
            _id = "{}.{}".format(_sta['@netid'], _sta['@code'])

            # Each station is a dictionary of attributes, and contains
            # another list for the components
            station = {'id': _id, 'name': _sta['@name'], 'code': _sta['@code'],
                       'netid': _sta['@netid'], 'source': _sta['@source'],
                       'insttype': _sta['@insttype'], 'components': [],
                       'lat': float(_sta['@lat']), 'lon': float(_sta['@lon']),
                       'components': []}
            
            # Create a station-level dictionary (in fact, a wrapper 
            # around the dictionary)
            station_node = ESMShakeMapStationNode(data_dict=station)

            # Add the station node to the main data structure
            esm_shakemap_data.stations.append(station_node)

            # Each component is again a dictionary
            for _comp in _sta['comp']:
                component = {'name': _comp['@name'],
                             'depth': float(_comp['@depth']),
                             'acc': float(_comp['acc']['@value']),
                             'accflag': int(_comp['acc']['@flag']),
                             'vel': float(_comp['vel']['@value']),
                             'velflag': int(_comp['vel']['@flag']),
                             'psa03': float(_comp['psa03']['@value']),
                             'psa03flag': int(_comp['psa03']['@flag']),
                             'psa10': float(_comp['psa10']['@value']),
                             'psa10flag': int(_comp['psa10']['@flag']),
                             'psa30': float(_comp['psa30']['@value']),
                             'psa30flag': int(_comp['psa30']['@flag'])}

                # Create a channel-level dictionary
                channel_node = ESMShakeMapComponentNode(data_dict=component)

                # Add the channel node to the station node
                station_node.components.append(channel_node)

        # Pass the main data structure back to the caller
        return esm_shakemap_data
    
    def parse(self, data):
        """
        Calls the internal parse method for format="event_dat" option
        if the data is successfully validated.
        """
        if data and self.validate(data):
            return self._parse(data)
        else:
            raise ValueError("Invalid data. The content is not " +
                             "a valid ESM Shakemap XML file.")        

    def validate(self, data):
        """Check the content of the data."""
        return True
    
    def parse_earthquake(self, data):
        """ 
        Parse the data returned by the ESM ShakeMap web service 
        when format='event'. 
        """
        if data and self.validate(data):
            # Store the original content
            self.set_original_content(content=data)

            # Convert the XML content to a dictionary.
            xml_content = xmltodict.parse(data)

            eq = xml_content['earthquake']
            event_data = {'id': eq['@id'], 'catalog': eq['@catalog'], 
                          'lat': float(eq['@lat']), 'lon': float(eq['@lon']), 
                          'depth': float(eq['@depth']), 'mag': float(eq['@mag']), 
                          'year': eq['@year'], 'month': eq['@month'],
                          'day': eq['@day'], 'hour': eq['@hour'], 
                          'minute': eq['@minute'], 'second': eq['@second'], 
                          'timezone': eq['@timezone'], 'time': eq['@time'], 
                          'locstring': eq['@locstring'], 'netid': eq['@netid'], 
                          'network': eq['@network'], 'created': eq['@created']}
            
            esm_shakemap_data = ESMShakeMapData(event_data)

            return esm_shakemap_data
        
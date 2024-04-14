# -*-coding: utf-8 -*-
from .base_client import BaseClient, MissingRequiredOption
from .services import EMSCFeltReportWebService
from .services.feltreport_data import FeltReportItensityData

class EMSCFeltReportClient(BaseClient):
    """
    This class encapsulates the worker class for the EMSC felt report
    web service and its data structure(s), both for intensities and
    event data. 
    """
    def __init__(self):
        super().__init__()
        
        # Provider
        self.agency = "EMSC"
        
        # Main service url
        self.base_url = "https://www.seismicportal.eu/testimonies-ws/"
        
        # Query end point
        self.end_point = "api"
        
        # Version of the service, if applicable
        self.version = "1.1"
        
        # Options for querying the felt reports. The web service
        # will return a zip file.
        self.felt_report_options = {'includeTestimonies': 'true'}

        # Options for querying the event data. The web service
        # will return a json file.
        self.event_data_options = {'includeTestimonies': 'false'}
        
        # Initialize the web service client.
        if self.get_web_service() is None:
            self.create_web_service()

    def set_event_id(self, event_id):
        """ Set the event id. """
        self.felt_report_options['unids'] = "[" + event_id + "]"
        self.event_data_options['unids'] = "[" + event_id + "]"

    def get_event_id(self):
        """ 
        Return the event id but strip the brackets that were added
        for the web service compatibiity. 
        """
        return self.felt_report_options['unids'].replace(
            '[', '').replace(']', '')
    
    def create_web_service(self)->EMSCFeltReportWebService:
        """ Creates a new EMSC felt report web service client. """
        self.ws_client = EMSCFeltReportWebService(
            agency=self.agency, base_url=self.base_url, 
            end_point=self.end_point, version=self.version)

        # Return the client for further use in case
        # the method is called directly.
        return self.ws_client
            
    
    def get_feltreports(self):
        """ Return the felt reports. Felts reports are designed to have
        more than one event. The event id is the key for the dictionary 
        for this event."""
        # This is actually a dict that we already wrapped around.
        # Create a new FeltReportItensityData object and return it
        # so that we can continue to use the same interface.
        feltreport_dict = \
            super().get_feltreports()[self.get_event_id()]
        
        return FeltReportItensityData(feltreport_dict)
    
    def query(self, event_id=None, **other_options):
        """ Query the web service for earthquake information. """
        # Check and set options that are free to modify.
        # The check below adds the event_id into the options
        # for both back ends.
        if event_id is not None:
            self.set_event_id(event_id)
        else:
            raise MissingRequiredOption(
                "Missing required option: event_id")

        # Query the web service for the felt reports.
        _url = self.ws_client.build_url(**self.felt_report_options)
        _code, _feltreport_data = self.ws_client.query(url=_url)
        self.set_feltreports(_feltreport_data)

        # Query the web service for the event parameters.
        _url = self.ws_client.build_url(**self.event_data_options)
        _code, _event_data = self.ws_client.query(url=_url)
        self.set_event_data(_event_data)

        return _code, _event_data, _feltreport_data
    
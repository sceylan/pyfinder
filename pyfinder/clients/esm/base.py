#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class Client:
    """ Manager class for accessing all ESM web services via http. """
    def __init__(self):
        pass


class InvalidQueryOption(Exception):
    pass


class ClientBase:
    def __init__(self, agency=None, web_service=None):
        self.agency = agency
        self.web_service = web_service

    def get_agency(self):
        return self.agency

    def set_agency(self, agency):
        self.agency = agency

    def get_web_service(self):
        return self.web_service

    def set_web_service(self, service):
        self.web_service = service

    def validate_options(self, **options):
        """
        Checks whether all the given options are supported by the relevant
        web service. Each subclass of ClientBase is required supply a list
        of the options via the get_supported_ws_options() abstract method.
        """
        for option in options:
            if option not in self.get_supported_ws_options():
                raise InvalidQueryOption(
                    "`{}` is not a valid query option for {}-{}".format(
                        option, self.get_agency(), self.get_web_service()))

    @abstractmethod
    def get_supported_ws_options(self):
        return None

    @abstractmethod
    def build_url(self, **options):
        pass

    @abstractmethod
    def parse(self, file_like_obj):
        pass

    @abstractmethod
    def query(self, **options):
        pass

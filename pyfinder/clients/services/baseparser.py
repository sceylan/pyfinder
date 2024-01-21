# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """ Base class for all parsers."""
    def __init__(self):
        # Stores the original content of the data passed for parsing.
        self.original_content = None
        
        super().__init__()

    def set_original_content(self, content):
        """ Set the original content of the data."""
        self.original_content = content

    def get_original_content(self):
        """ Return the original content of the data."""
        return self.original_content
    
    @abstractmethod
    def parse(self, data):
        """
        Abstract method for parsing data.

        Parameters:
        - data: The data to be parsed.

        Returns:
        - Parsed result.
        """
        pass

    @abstractmethod
    def validate(self, data):
        """
        Abstract method for validating data before parsing.

        Parameters:
        - data: The data to be validated.

        Returns:
        - True if data is valid, False otherwise.
        """
        pass

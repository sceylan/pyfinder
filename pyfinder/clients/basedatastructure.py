# -*- coding: utf-8 -*-
class BaseDataStructure:
    """ 
    Base class for the data structure used to store the data retrieved
    from the web services. 
    
    There is no strict definition of the data as it depends on the particular 
    web service that is being used. Subclasses of this class should be
    created for each web service and deal with the fields internally. 
    Most of the web services provide data for 3-components as well as some
    additional data, such as event_id, at the event level. In these cases,
    the subclass should have multiple dictionaries, one for the event level
    and one for each component.

    The data structure itsels is a dictionary. This class allows to add 
    and remove fields to the dictionary. Data can be accessed via the dot 
    notation or the set() and get() methods.
    
    >>> data = BaseDataStructure()
    >>> data.add_field('eventid')
    >>> data.add_field('event_lat')

    Set and get using the dot notation
    >>> data.eventid = '20170524_0000045'
    >>> data.eventid
    '20170524_0000045'

    Or, set and get using the set() and get() methods
    >>> data.set('event_lat', 38.8)
    >>> data.get('event_lat')
    38.8
    """
    def __init__(self, **kwargs):
        # dict to store the data
        self._data = kwargs

    def add_field(self, field_name, default_value=None):
        if field_name not in self._data:
            self._data[field_name] = default_value
        else:
            raise ValueError(f"Field '{field_name}' already exists.")

    def remove_field(self, field_name):
        if field_name in self._data:
            del self._data[field_name]
        else:
            raise ValueError(f"Field '{field_name}' does not exist.")
        
    def data(self):
        """ 
        Return the data dictionary itself in case the rather
        simple functionality wrapped in this class is not enough.
        """
        return self._data
    
    def get(self, field_name):
        try:
            return self._data.get(field_name)
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}'"
                                 " object has no attribute '{field_name}'")
    
    def set(self, field_name, value):
        if field_name in self._data:
            self._data[field_name] = value
        else:
            raise ValueError(f"Field '{field_name}' does not exist.")

    def __getattr__(self, attr):
        """ Override the __getattr__ method to allow getting attributes"""
        try:
            return self._data[attr]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}'"
                                 " object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        """ Override the __setattr__ method to allow setting attributes"""
        if "_data" in self.__dict__ and attr in self._data:
            self._data[attr] = value
        else:
            super().__setattr__(attr, value)

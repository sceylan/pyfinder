# -*- coding: utf-8 -*-
import copy

class BaseDataStructure:
    """ 
    Base class for the data structure used to store the data retrieved
    from the web services. 
    
    There is no strict definition of the data structure as it depends on 
    the particular web service that is being used. Subclasses of this 
    class should be created for each web service and deal with the fields 
    internally. Most of the web services provide data for 3-components 
    as well as some additional data, such as event_id, at the event level. 
    In these cases, the subclass chould have multiple dictionaries, one for 
    the event level and one for each component. Alternatively, the nested 
    data structure can be stored as lists of dictionaries under a single key 
    in the main dictionary.

    The data structure itself is a dictionary. This class allows to add 
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
    def __init__(self, data_dict=None, **kwargs):
        # dict to store the data. Use a copt so that
        # the original data is not modified outside.
        if data_dict is not None:
            self._data = copy.deepcopy(data_dict)
        else:
            self._data = {}

    def add_field(self, field_name, value=None):
        """ Add a new field to the data dictionary."""
        if field_name not in self._data:
            self._data[field_name] = value
        else:
            raise ValueError(f"Field '{field_name}' already exists.")

    def remove_field(self, field_name):
        """ Remove a field from the data dictionary."""
        if field_name in self._data:
            del self._data[field_name]
        else:
            raise ValueError(f"Field '{field_name}' does not exist.")
        
    def keys(self):
        """Mimic the dict.keys() method."""
        if self._data is None:
            return []
        else:
            return self._data.keys()
    
    def values(self):
        """Mimic the dict.values() method."""
        if self._data is None:
            return []
        else:
            return self._data.values()
        
    def items(self):
        """Mimic the dict.items() method."""
        if self._data is None:
            return []
        else:
            return self._data.items()
        
    def _get(self, key):
        """ 
        Internal get method that returns the value of the given key. 
        If the key does not exist, returns None. Shortcut for get() 
        with try-except block because get() needs to raise an exception 
        when the key does not exist if data is manipulated outside 
        this class or its sub-classes.
        """
        try:
            return self.get(key)
        except: 
            return None
        
    def get_data(self):
        """ 
        Return the data dictionary itself in case the rather
        simple functionality wrapped in this class is not enough.
        """
        return self._data
    
    def set_data(self, data_dict):
        """ 
        Set the whole data dictionary. Probably more useful than
        individual add_field() method when the output of a 
        web service is parsed.
        """
        if isinstance(data_dict, dict):
            self._data = copy.deepcopy(data_dict)
        else:
            raise ValueError("Data must be a dictionary, not a " + str(type(data_dict)))
        
    def get(self, field_name):
        """ Return the value of a field. """
        try:
            return self._data.get(field_name)
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}'"
                                 " object has no attribute '{field_name}'")
    
    def set(self, field_name, value, add_if_not_exist=False):
        """ 
        Set the value of a field. Allows to force adding a field
        with if_not_exist=True when a field does not exist.
        """
        if field_name in self._data:
            self._data[field_name] = value
        else:
            if add_if_not_exist:
                self.add_field(field_name, value)
            else:
                raise KeyError(f"Field '{field_name}' does not exist.")

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

    def __getitem__(self, key):
        if self._data:
            return self._data[key]

    def __setitem__(self, key, value):
        if self._data:
            self._data[key] = value

    def __delitem__(self, key):
        if self._data:
            del self._data[key]

    def __str__(self):
        return str(self._data)

if __name__ == "__main__":
    dst = BaseDataStructure()

    dst.add_field('eventid')
    dst.eventid = '20170524_0000045'
    print(dst.eventid)

    dst.testField = "test field"
    print(dst.testField)

    dst['testField2'] = "test field 2"
    print(dst['testField2'])

    dst.set('event_lat', 38.8, add_if_not_exist=True)
    print(dst.get('event_lat'))
    
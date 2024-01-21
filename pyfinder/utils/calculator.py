# -*- coding: utf-8 -*-
import numpy as np

class Calculator(object):
    """ Utility class for methods to implement calculations. """
    @staticmethod
    def percent_g_to_cm_s2(percent_g, average_g=980.665):
        """ 
        Convert percent g to cm/s^2. Needed for the accelerations in
        the ESM shakemap web service acceleration output.
        """
        # Acceleration from percentage using the average acceleration 
        # due to gravity in cm/s^2
        return (percent_g * 0.01) * average_g


    @staticmethod
    def haversine(lat1, lon1, lat2, lon2, radius_in_km=6371.0):
        """ 
        Calculate the great circle distance between two points 
        on the earth using the Haversine formula.
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Calculate the distance in km and return it
        distance = radius_in_km * c
        return distance

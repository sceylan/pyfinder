# -*- coding: utf-8 -*-
import numpy as np


class Calculator(object):
    """Utility class for methods to implement calculations."""

    @staticmethod
    def percent_g_to_cm_s2(percent_g, average_g=980.665):
        """Convert percent g to cm/s^2. Needed for the accelerations in
        the ESM shakemap web service acceleration output."""
        # Acceleration from percentage using the average acceleration
        # due to gravity in cm/s^2
        return (percent_g * 0.01) * average_g

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2, radius_in_km=6371.0):
        """Calculate the great circle distance between two points
        on the earth using the Haversine formula."""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat / 2) ** 2 + \
            np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Calculate the distance in km and return it
        distance = radius_in_km * c
        return distance

    @staticmethod
    def I_to_PGA_Wordon2012(sta_I, alpha1=1.78, beta1=1.557, alpha2=-1.60,
                            beta2=3.7, thres=4.22):
        # If a list is passed, convert it to a numpy array
        if isinstance(sta_I, list):
            sta_I = np.array(sta_I)

        # Calculate the log PGA using the Wordon et al. (2012) method
        sta_logPGA = np.where(sta_I <= thres, 
                              (sta_I - alpha1) / beta1, 
                              (sta_I - alpha2) / beta2)

        # Return the log PGA
        return sta_logPGA

    def I_Allen2012_Rhypo(eq_mag, eq_depth, sta_dist,
                          c0=2.085, c1=1.428, c2=-1.402,
                          c4=0.078, m1=-0.209, m2=2.042,
                          Imin=3):
        RM = m1 + m2 * np.exp(eq_mag - 5)
        R_hypo = np.sqrt(eq_depth ** 2 + sta_dist ** 2)
        I_sim = c0 + (c1 * eq_mag) + \
            c2 * np.log(np.sqrt(R_hypo ** 2 + RM ** 2)) + \
                c4 * np.log(R_hypo / 50)
        
        idx = (R_hypo <= 50)
        I_sim[idx] = c0 + (c1 * eq_mag) + \
            c2 * np.log(np.sqrt(R_hypo[idx] ** 2 + RM ** 2))
        
        max_dist = np.sqrt(
            (np.exp(
                (Imin - c0 - (c1 * eq_mag) - c4 * np.log(R_hypo / 50)) \
                    / c2)) ** 2 - RM ** 2)

        return I_sim, max_dist

    


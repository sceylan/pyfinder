# -*- coding: utf-8 -*-

class Calculator(object):
    """ Utility class for methods to implement calculations. """
    @staticmethod
    def percent_g_to_cm_s2(percent_g):
        """ 
        Convert percent g to cm/s^2. Needed for the accelerations in
        the ESM shakemap web service acceleration output.
        """
        # Average acceleration due to gravity in cm/s^2
        g = 980.665  
        acceleration_cm_s2 = (percent_g * 0.01) * g
        return acceleration_cm_s2
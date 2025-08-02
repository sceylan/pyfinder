# -*- coding: utf-8 -*-
"""
Module to locate regions based on latitude and longitude.
Uses a shapefile of country boundaries to determine the region for given coordinates.
"""
import geopandas as gpd
from shapely.geometry import Point
from pyfinderconfig import pyfinderconfig

class RegionLocator:
    def __init__(self):
        shapefile_path = pyfinderconfig["shakemap"]["country-borders-shapefile"]

        # Load shapefile once (can be reused)
        self.countries = gpd.read_file(shapefile_path)[['ISO_A2', 'geometry']]
        self.countries['ISO_A2'] = self.countries['ISO_A2'].str.lower()

    def get_region(self, lat, lon):
        """Return the two-letter country code for a point.
        If the point is offshore, return the nearest country's code."""
        if lat is None or lon is None:
            return "unknown"
        
        # Create a Point object for the given coordinates
        point = Point(lon, lat)
        
        # Check if inside a country's polygon
        matches = self.countries[self.countries.contains(point)]
        if not matches.empty:
            return matches.iloc[0]['ISO_A2'].lower()
        
        # Offshore -> find nearest country's boundary
        self.countries['distance'] = self.countries.distance(point)
        nearest = self.countries.loc[self.countries['distance'].idxmin()]

        # If no nearest country found, return "unknown"
        if nearest.empty:
            return "unknown"
        
        # Return the two-letter country code of the nearest country
        return nearest['ISO_A2'].lower()
    
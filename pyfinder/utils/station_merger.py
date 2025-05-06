# -*- coding: utf-8 -*-
""" 
Utility classes used when merging station/amplitude data from different web services. 
"""
from typing import TypedDict, List

class RawStationMeasurement(TypedDict):
    """
    A dictionary to hold the raw station measurement data.
    """
    latitude: float
    longitude: float
    network: str
    station: str
    location: str 
    channel: str
    pga: float  # in cm/s/s
    timestamp: float 
    source: str  # "ESM" or "RRSM" etc.


class StationMerger:
    def merge(self, esm_data: List[RawStationMeasurement], 
              rrsm_data: List[RawStationMeasurement]) -> List[RawStationMeasurement]:
        """Merge two station lists, giving priority to ESM on conflicts."""
        merged = {}
        
        # Index RRSM data first
        for sta in rrsm_data:
            key = self._make_key(sta)
            merged[key] = sta

        # Overwrite with ESM (priority)
        for sta in esm_data:
            key = self._make_key(sta)
            merged[key] = sta

        # Sort merged stations by descending PGA
        return sorted(merged.values(), key=lambda x: x["pga"], reverse=True)

    def _make_key(self, sta: RawStationMeasurement) -> str:
        """Use SNCL or coordinates as key."""
        # Prefer SNCL if all fields exist
        if all(sta.get(k) for k in ["network", "station", "location", "channel"]):
            return f"{sta['network']}.{sta['station']}.{sta['location']}.{sta['channel']}"
        else:
            # Fall back to rounded lat/lon (avoid float drift)
            return f"{round(sta['latitude'], 4)}_{round(sta['longitude'], 4)}"
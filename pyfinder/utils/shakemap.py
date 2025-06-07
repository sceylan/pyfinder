# -*- coding: utf-8 -*-
""" Module to manage the shakemap input files from FinDer solution."""

# ShakeMapExporter: exports ShakeMap-compatible event.xml and stationlist.json from a FinderSolution
import os
import json
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, ElementTree
import subprocess
from finderutils import FinderSolution
import logging
import zipfile


# --------------------------------------------
# ShakeMapExporter utility for exporting ShakeMap-compatible files
# --------------------------------------------
class ShakeMapExporter:
    """
    A utility class to export ShakeMap-compatible input files from a FinderSolution.
    It generates event.xml and stationlist.json in a temporary or specified directory.
    """

    def __init__(self, solution: FinderSolution, logger=None,
                 output_dir: str = None, augmented_id: str = None):
        # Get the finder-manager logger
        if logger is None:
            self.logger = logging.getLogger("FinDerManager")
        else:
            self.logger = logger

        # Validate that the solution is a FinderSolution instance. Do not react to the
        # FinderSolution being wrong, but rather log it so that we can debug it.
        if solution is None:
            self.logger.error("No solution provided to ShakeMapExporter.")
        elif not isinstance(solution, FinderSolution):
            self.logger.error(f"Provided solution {type(solution)} is not a {FinderSolution.__module__} instance.")
            
        self.logger.info(f"ShakeMapExporter initialized with FinderSolution: {solution.get_description()}")
        self.solution = solution

        # Set the augmented ID: This is the eventID with delay appended
        # to it. This is used to create a unique event ID for ShakeMap.
        self.augmented_id = augmented_id
        if self.augmented_id is not None:
            self.logger.info(f"Augmented ID set to: {self.augmented_id}")
        else:
            self.logger.info("No augmented ID provided.")

        # Create a default output directory in the user's home. Use the augmented ID 
        # if provided, otherwise use the event ID or finder event ID.
        _id_to_use = self.augmented_id or self.solution.get_event_id() or self.solution.get_finder_event_id()
        
        self.output_dir = output_dir or os.path.join(
            os.path.expanduser("~"), "shakemap_profiles", "default", "data", _id_to_use, "current"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(f"ShakeMapExporter output directory: {self.output_dir}")

    def archive_products(self, target_base_dir=None, extensions=("json", "jpg", "jpeg")):
        """ 
        Archive ShakeMap products into a zip file under the given target_base_dir. 
        The files are filtered by the provided extensions to avoid large file sizes.
        In the current implementation, the default extensions are json, jpg, and jpeg;
        no wildcards are accepted.
        """
        # Check if target_base_dir is provided
        if target_base_dir is None:
            raise ValueError("target_base_dir for the zip archive must be provided")  # <<==

        # Ensure products folder exists. This is where we copy the files to.
        my_products_dir = os.path.join(target_base_dir, "shakemap_products")
        os.makedirs(my_products_dir, exist_ok=True)

        # Where the original files are
        shmap_products_dir = os.path.join(self.output_dir, "products")

        # Check if the original products directory exists
        if not os.path.exists(shmap_products_dir):  # <<==
            self.logger.warning(f"ShakeMap products directory does not exist: {shmap_products_dir}") 
            return None 

        # Create a zip file with the products
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"shakemap_output_{datetime_str}.zip"  # <<==
        zip_path = os.path.join(my_products_dir, zip_filename)

        # Zip everything in the products directory that matches the extensions
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(shmap_products_dir):
                for file in files:
                    if file.lower().endswith(extensions):
                        file_path = os.path.join(root, file)
                        # Create a relative path to the file
                        relative_path = os.path.relpath(file_path, shmap_products_dir)

                        zipf.write(file_path, relative_path)
                        self.logger.info(f"Added {file_path} to zip as {relative_path}")
        self.logger.info(f"Created zip file: {zip_path}")

        # Return the path to the zip file
        return zip_path


    def export_all(self):
        """Exports both event.xml and stationlist.json as well as rupture.json """
        event_path = self._write_event_xml()
        # station_path = self._write_stationlist_json()
        rupture_path = self._write_rupture_json()
        event_dat_xml_path = self._write_event_dat_xml()

        # Ensure products dir exists
        products_dir = os.path.join(self.output_dir, "products")
        os.makedirs(products_dir, exist_ok=True)

        self.logger.info(f"ShakeMap files written to {self.output_dir}")

        return {
            "event.xml": event_path,
            "stationlist.json": event_dat_xml_path, #station_path,
            "rupture.json": rupture_path,
            "output_dir": self.output_dir
        }


    def _write_rupture_json(self):
        rupture = self.solution.get_rupture()
        if rupture is None:
            return None

        # Create closed loop of points for MultiPolygon
        coords = [[lon, lat, depth] for lat, lon, depth in rupture.get_points()]
        if coords and coords[0] != coords[-1]:
            coords.append(coords[0])  # Ensure loop is closed

        rupture_data = {
            "type": "FeatureCollection",
            "metadata": {
                "reference": "Generated by FinDer during pyfinder runtime"
            },
            "features": [{
                "type": "Feature",
                "properties": {
                    "rupture type": "rupture extent"
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [[coords]]
                }
            }]
        }

        path = os.path.join(self.output_dir, "rupture.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rupture_data, f, indent=2)
        return path
    
    def _write_event_dat_xml(self):
        """Writes event_dat.xml using the standard ShakeMap XML format for station data."""
        from xml.dom.minidom import Document
        import os
        from datetime import datetime

        if self.solution.get_channels() is None:
            self.logger.error("No channels found in the solution.")
            return None

        doc = Document()
        root = doc.createElement("stationlist")
        root.setAttribute("created", datetime.now().isoformat())
        root.setAttribute("xmlns", "ch.ethz.sed.shakemap.usgs.xml")
        doc.appendChild(root)

        for ch in self.solution.get_channels():
            pga = ch.get_pga()
            pga_g = pga / 9.806 if pga is not None else None
            if pga_g is None:
                continue

            station = doc.createElement("station")
            station.setAttribute("code", ch.get_station_code())
            station.setAttribute("name", ch.get_station_code())
            station.setAttribute("insttype", ch.get_channel_code())
            station.setAttribute("lat", str(ch.get_latitude()))
            station.setAttribute("lon", str(ch.get_longitude()))
            station.setAttribute("source", ch.get_network_code())
            station.setAttribute("commtype", "DIG")
            station.setAttribute("netid", ch.get_network_code())
            station.setAttribute("loc", ch.get_location_code())

            comp = doc.createElement("comp")
            comp.setAttribute("name", f"{ch.get_channel_code()}N")

            acc = doc.createElement("acc")
            acc.setAttribute("value", f"{pga_g:.5f}")
            acc.setAttribute("flag", "0")

            comp.appendChild(acc)
            station.appendChild(comp)
            root.appendChild(station)

        path = os.path.join(self.output_dir, "event_dat.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc.toprettyxml(indent="  "))

        self.logger.info(f"event_dat.xml written to {path}")
        return path
    
    
    def _write_event_xml(self):
        event = self.solution.get_event()
        root = Element("earthquake")
        root.set("event_id", self.solution.get_event_id() or self.solution.get_finder_event_id())
        root.set("id", self.solution.get_finder_event_id() or self.solution.get_event_id())
        root.set("netid", "FinDer")
        root.set("mag", str(event.get_magnitude()))
        root.set("lat", str(event.get_latitude()))
        root.set("lon", str(event.get_longitude()))
        root.set("depth", str(event.get_depth()))
        root.set("time", datetime.fromtimestamp(event.get_origin_time_epoch(), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        root.set("locstring", "FinDer Origin")
        root.set("event_type", "ACTUAL")

        tree = ElementTree(root)
        path = os.path.join(self.output_dir, "event.xml")
        tree.write(path, encoding="utf-8", xml_declaration=True)
        return path

    def _write_stationlist_json(self):
        features = []

        if self.solution.get_channels() is None:
            self.logger.error("No channels found in the solution.")

        for ch in self.solution.get_channels():
            pga = ch.get_pga()
            pga_g = pga / 9.81 if pga is not None else None
            # Build properties dict, extending with pgm and units field
            properties = {
                "network": ch.get_network_code(),
                "netid": ch.get_network_code(),
                "intensity_flag": "",
                "mmi_from_pgm": [],
                "commType": "UNK",
                "intensity": None,
                "pgv": None,
                "source": ch.get_network_code(),
                "instrumentType": "OBSERVED",
                "station_type": "seismic",
                "code": f"{ch.get_network_code()}.{ch.get_station_code()}",
                "name": ch.get_station_code(),
                "pga": pga_g,
                "pgm": {
                    "pga": {
                        "value": pga_g,
                        "units": "g",
                        "flag": 0
                    }
                } if pga_g is not None else {},
                "units": {
                    "pga": "g"
                } if pga_g is not None else {},
                "intensity_stddev": None,
                # "distance": ch.get_distance_km() or 0.0,
                # "distances": {
                #     "ry0": ch.get_distance_km() or 0.0,
                #     "rrup": ch.get_distance_km() or 0.0,
                #     "rjb": ch.get_distance_km() or 0.0,
                #     "rx": 0.0,
                #     "rhypo": ch.get_distance_km() or 0.0
                # },
                "location": ch.get_location_code(),
                "channels": [
                    {
                        "name": f"{ch.get_location_code()}.{ch.get_channel_code()}",
                        "amplitudes": [
                            {
                                "name": "pga",
                                "value": pga_g,
                                "units": "g",
                                "flag": "0",
                                "ln_sigma": 0
                            }
                        ] if pga_g is not None else []
                    }
                ],
                "predictions": []
            }
            feature = {
                "type": "Feature",
                "id": f"{ch.get_network_code()}.{ch.get_station_code()}",
                "geometry": {
                    "type": "Point",
                    "coordinates": [ch.get_longitude(), ch.get_latitude()]
                },
                "properties": properties
            }
            features.append(feature)

        collection = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "created": datetime.now().isoformat() + "Z",
                "source": "pyfinder"
            }
        }

        path = os.path.join(self.output_dir, "stationlist.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2)
        return path


# --------------------------------------------
# ShakeMapTrigger utility for running ShakeMap
# --------------------------------------------
class ShakeMapTrigger:
    """ Utility class to trigger ShakeMap from a set of exported files. """
    def __init__(self, event_id, event_xml, stationlist_path, rupture_path=None, 
                 shake_cmd='shake', logger=None):
        self.event_id = event_id
        self.event_xml = event_xml
        self.stationlist_path = stationlist_path
        self.rupture_path = rupture_path
        self.shake_cmd = shake_cmd
        self.logger = logger or logging.getLogger("FinDerManager")

    def validate_inputs(self):
        if not os.path.isfile(self.event_xml):
            raise FileNotFoundError(f"Missing event file: {self.event_xml}")
        if not os.path.isfile(self.stationlist_path):
            raise FileNotFoundError(f"Missing stationlist file: {self.stationlist_path}")
        if self.rupture_path and not os.path.isfile(self.rupture_path):
            raise FileNotFoundError(f"Missing rupture file: {self.rupture_path}")

    def run(self):
        self.validate_inputs()
        cmd = [
            self.shake_cmd,
            "--force",  # force overwrite of existing files
            "-d", self.event_id,  # positional argument for event ID
            "select", "assemble",
            "-c", "pyFinder",
            "model", "contour", "mapping", "stations",  "gridxml"
        ]

        self.logger.info(f"Running ShakeMap: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("ShakeMap triggered successfully.")
            self.logger.debug(result.stdout)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ShakeMap failed: {e.stderr}")
            raise

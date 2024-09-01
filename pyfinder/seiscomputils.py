# -*- coding: utf-8 -*-
""" Manager to serialize FinDer solution and amplitudes to SeisComp. """

import subprocess
import seiscomp.client as sc_client
import seiscomp.core as sc_core
import seiscomp.datamodel as sc_dm  
import seiscomp.io as sc_io
from seiscomp.datamodel import strongmotion  

class FinderToSeiscomp:
    def __init__(self, event_id):
        self.event_id = event_id
        self.event = None
        self.origin = None
        self.magnitude = None
        self.database = None
        self.connection = None
        self.amplitudes = []  # To store PGA amplitudes
        self.message_groups = []  # List of specific messaging queues to notify

    def check_seiscomp_running(self):
        """Check if SeisComp is running by looking for key processes."""
        try:
            output = subprocess.check_output(["seiscomp", "status"], stderr=subprocess.STDOUT)
            if b"running" in output:
                print("SeisComp is running.")
                return True
            else:
                print("SeisComp is not running.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to check SeisComp status: {e.output.decode()}")
            return False

    def restart_seiscomp(self):
        """Attempt to restart SeisComp."""
        try:
            subprocess.check_call(["seiscomp", "start"])
            print("SeisComp restarted successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart SeisComp: {e.output.decode()}")
            return False

    def connect_to_database(self, db_uri):
        """Connect to the SeisComp database."""
        if not self.check_seiscomp_running():
            if not self.restart_seiscomp():
                print("Operation failed: Unable to restart SeisComp.")
                return False

        # Create a DatabaseInterface object using the factory
        db_interface = sc_io.DatabaseInterface.Create(db_uri)
        if not db_interface:
            raise ConnectionError(f"Failed to create database interface for URI: {db_uri}")

        # Pass the DatabaseInterface object to the DatabaseArchive constructor
        self.database = sc_dm.DatabaseArchive(db_interface)
        if not self.database.open(db_uri):
            raise ConnectionError(f"Failed to connect to database at {db_uri}")
        print(f"Connected to database at {db_uri}")
        return True

    def connect_to_messaging(self, message_groups):
        """Connect to SeisComp messaging system and set target message groups."""
        if not self.check_seiscomp_running():
            if not self.restart_seiscomp():
                print("Operation failed: Unable to restart SeisComp.")
                return False

        self.connection = sc_client.Connection()
        if not self.connection.open():
            raise ConnectionError("Failed to connect to SeisComp messaging system.")
        
        # Set message groups (queues) for notifications
        self.message_groups = message_groups
        print(f"Connected to SeisComp messaging system, targeting groups: {self.message_groups}")
        return True

    def create_event(self, finder_location, origin_time, web_service_name):
        """Create an event in SeisComp's data model."""
        self.event = sc_dm.Event.Create()
        self.event.setPublicID(f"smi:finder/{self.event_id}")
        self.event.setPreferredOriginID(f"smi:finder/{self.event_id}/origin")
        self.event.setCreationInfo(self.create_creation_info())

        # Add a comment to store the web service name
        self.add_web_service_comment(self.event, web_service_name)

        self.create_origin(finder_location, origin_time, web_service_name)
        self.create_magnitude()

        self.event.setPreferredMagnitudeID(self.magnitude.publicID())

        return self.event

    def create_origin(self, finder_location, origin_time, web_service_name):
        """Create the origin object from FinDer data."""
        lat, lon, depth = finder_location

        self.origin = sc_dm.Origin.Create(f"smi:finder/{self.event_id}/origin")
        self.origin.setLatitude(sc_dm.RealQuantity(lat))
        self.origin.setLongitude(sc_dm.RealQuantity(lon))
        self.origin.setDepth(sc_dm.RealQuantity(depth * 1000))  # Depth in meters

        # Convert the origin_time string to a Time object
        origin_time_obj = sc_core.Time.FromString(origin_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Wrap the Time object in a TimeQuantity object
        time_quantity = sc_dm.TimeQuantity(origin_time_obj)
        self.origin.setTime(time_quantity)

        self.origin.setEvaluationMode(sc_dm.EvaluationMode.MANUAL)
        self.origin.setCreationInfo(self.create_creation_info())

        # Add a comment to store the web service name
        self.add_web_service_comment(self.origin, web_service_name)

    def create_magnitude(self):
        """Create a magnitude object from PGA data."""
        mag_value = self.calculate_magnitude_from_pga()

        self.magnitude = sc_dm.Magnitude.Create(f"smi:finder/{self.event_id}/magnitude")
        self.magnitude.setMagnitude(sc_dm.RealQuantity(mag_value))
        self.magnitude.setType("ML")
        self.magnitude.setOriginID(self.origin.publicID())
        self.magnitude.setCreationInfo(self.create_creation_info())

    def create_creation_info(self):
        """Create a CreationInfo object."""
        ci = sc_dm.CreationInfo()
        ci.setAgencyID("FinderApp")  # Your institution or agency
        ci.setAuthor("FinderToSeiscomp")
        return ci

    def add_rupture_polygon(self, polygon_coords):
        """Attach rupture polygon information as a comment to the event."""
        # Convert the polygon coordinates into a string representation
        polygon_str = "; ".join([f"({lat}, {lon})" for lat, lon in polygon_coords])
        
        # Create a comment object
        comment = sc_dm.Comment()
        comment.setText(f"Rupture Polygon: {polygon_str}")
        
        # Attach this comment to the origin
        self.origin.add(comment)

    def add_pga_amplitude(self, station_id, channel_code, pga_value, pga_time, web_service_name):
        """Add a PGA amplitude to the SeisComp event."""
        amplitude = sc_dm.Amplitude.Create()
        amplitude.setPublicID(f"smi:finder/{self.event_id}/amplitude/{station_id}/{channel_code}")
        amplitude.setAmplitude(sc_dm.RealQuantity(pga_value))
        amplitude.setType("PGA")
        amplitude.setUnit("m/s^2")
        amplitude.setTimeWindow(sc_dm.TimeWindow(sc_core.Time.FromString(pga_time, "%Y-%m-%dT%H:%M:%S.%fZ")))
        amplitude.setWaveformID(sc_dm.WaveformStreamID(networkCode=station_id.split('.')[0], stationCode=station_id.split('.')[1], channelCode=channel_code))
        
        # Set the web service name in MethodID
        amplitude.setMethodID(web_service_name)

        self.amplitudes.append(amplitude)

    def add_web_service_comment(self, obj, web_service_name):
        """Add a comment to the main SeisComp object."""
        comment = sc_dm.Comment()
        comment.setText(f"Queried from: {web_service_name}")
        obj.add(comment)

    def dump_to_database(self):
        """Dump the event and associated data to the SeisComp database."""
        if not self.database:
            raise RuntimeError("Database connection not established.")
        
        self.database.writeObject(self.origin)
        self.database.writeObject(self.magnitude)
        self.database.writeObject(self.event)
        
        for amplitude in self.amplitudes:
            self.database.writeObject(amplitude)

        print("Event and amplitudes successfully written to the database.")

    def notify_messaging_system(self):
        """Notify the specific SeisComp messaging groups."""
        if not self.connection:
            raise RuntimeError("Messaging connection not established.")

        # Send messages to specific message groups
        for group in self.message_groups:
            self.connection.send(self.origin, group)
            self.connection.send(self.magnitude, group)
            self.connection.send(self.event, group)
            for amplitude in self.amplitudes:
                self.connection.send(amplitude, group)

        print(f"Messages sent to SeisComp messaging groups: {self.message_groups}")

    def calculate_magnitude_from_pga(self):
        """Calculate magnitude from PGA (stub function)."""
        # Implement actual PGA-to-magnitude conversion
        return 5.5  # Example value

# This is an example until the module is ready to be included:
finder_data = {
    'location': (34.05, -118.25, 10.0),  # Example coordinates (lat, lon, depth in km)
    'origin_time': '2024-08-31T12:00:00.000Z',
    'polygon_coords': [(34.05, -118.25), (34.10, -118.20), (34.00, -118.30)],
    'event_id': 'finder_event_1234'
}

pga_data = [
    {'station_id': 'US.LSCT', 'channel_code': 'HNZ', 'pga_value': 0.2, 'pga_time': '2024-08-31T12:00:05.000Z'},
    {'station_id': 'US.LSCT', 'channel_code': 'HNN', 'pga_value': 0.3, 'pga_time': '2024-08-31T12:00:05.000Z'},
    {'station_id': 'US.LSCT', 'channel_code': 'HNE', 'pga_value': 0.25, 'pga_time': '2024-08-31T12:00:05.000Z'},
]

# Example message groups to notify
message_groups = ["GROUP1", "GROUP2"]

fts = FinderToSeiscomp(finder_data['event_id'])
if True: # fts.connect_to_database("mysql://user:password@localhost/seiscomp") and fts.connect_to_messaging(message_groups):
    fts.create_event(finder_data['location'], finder_data['origin_time'], "RRSM")
    fts.add_rupture_polygon(finder_data['polygon_coords'])
    
    # Add PGA amplitudes
    for pga in pga_data:
        fts.add_pga_amplitude(pga['station_id'], pga['channel_code'], pga['pga_value'], pga['pga_time'], "RRSM")
    
    fts.dump_to_database()
    fts.notify_messaging_system()
else:
    print("Failed to perform operations due to SeisComp not running.")

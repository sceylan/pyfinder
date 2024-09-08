import sys
import seiscomp.client as sc_client
import seiscomp.core as sc_core
import seiscomp.io as sc_io
import seiscomp.datamodel as sc_dm
import seiscomp.logging as sc_logging


class FinderToSeiscomp(sc_client.Application):
    def __init__(self, event_id):
        # Initialize the SeisComp application with argc and argv
        super().__init__(len(sys.argv), sys.argv)  

        # Enable messaging 
        self.setMessagingEnabled(True)

        # Enable database read/write access
        self.setDatabaseEnabled(True, True)

        # Disable daemon mode (application should terminate after run)
        self.setDaemonEnabled(False)

        self.event_id = event_id
        self.event = None
        self.origin = None
        self.magnitude = None
        self.amplitudes = []  # To store PGA amplitudes
        
    def create_command_line_description(self):
        """Handle command-line argument parsing."""
        super().create_command_line_description()

        # Add custom command-line arguments if needed
        self.commandline().add_option("custom", "event-id", "Specify the event ID")

    def init(self):
        """Initialize the application (messaging system, database, etc.)."""
        if not super().init():
            return False

        sc_logging.info("Initializing FinderToSeiscomp application")

        # Check database connection
        if not self.database():
            sc_logging.error("No database connection available")
            return False

        return True

    def run(self):
        """Main execution logic for the application."""
        sc_logging.info("Running FinderToSeiscomp")

        # Example finder data
        finder_data = {
            'location': (34.05, -118.25, 10.0),
            'origin_time': '2024-08-31T12:00:00.000Z',
            'polygon_coords': [(34.05, -118.25), (34.10, -118.20), (34.00, -118.30)],
            'event_id': self.event_id
        }

        pga_data = [
            {'station_id': 'US.LSCT', 'channel_code': 'HNZ', 'pga_value': 0.2, 'pga_time': '2024-08-31T12:00:05.000Z'},
            {'station_id': 'US.LSCT', 'channel_code': 'HNN', 'pga_value': 0.3, 'pga_time': '2024-08-31T12:00:05.000Z'},
            {'station_id': 'US.LSCT', 'channel_code': 'HNE', 'pga_value': 0.25, 'pga_time': '2024-08-31T12:00:05.000Z'},
        ]

        # Create event, origin, magnitude and add amplitudes
        self.fetch_or_create_event(finder_data['location'], finder_data['origin_time'], "RRSM")
        self.add_rupture_polygon(finder_data['polygon_coords'])

        for pga in pga_data:
            self.add_pga_amplitude(pga['station_id'], pga['channel_code'], pga['pga_value'], pga['pga_time'], "RRSM")

        # Dump to database
        # self.dump_to_database()

        # Notify messaging system
        self.notify_messaging_system()

        # Keep the application alive and listen for messages (optional)
        return True  # or return self.exec() if you want to keep it alive

    def fetch_or_create_event(self, finder_location, origin_time, web_service_name):
        """ Retreive and existing event or create a new one in SeisComp's data model."""
        query = self.query()

        # Attempt to fetch the event from the database
        event = query.getEvent(self.event_id)
        
        if event:
            sc_logging.info(f"Event {self.event_id} already exists in the database")
            self.event = event
            return event
        else:
            self.event = sc_dm.Event.Create()
            self.event.setPublicID(f"smi:finder/{self.event_id}")

        self.create_origin(finder_location, origin_time, web_service_name)
        self.create_magnitude()

        self.event.setPreferredOriginID(self.origin.publicID())
        self.event.setCreationInfo(self.create_creation_info())

        # Add a comment to store the web service name
        self.add_web_service_comment(self.event, web_service_name)

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

        self.origin.setCreationInfo(self.create_creation_info())

        # Add a comment to store the web service name
        self.add_web_service_comment(self.origin, web_service_name)

    def create_magnitude(self):
        """Create a magnitude object from PGA data."""
        mag_value = self.calculate_magnitude_from_pga()

        self.magnitude = sc_dm.Magnitude.Create(f"smi:finder/{self.event_id}/magnitude")
        self.magnitude.setMagnitude(sc_dm.RealQuantity(mag_value))
        self.magnitude.setType("ML")
        self.magnitude.setOriginID(self.origin.publicID())  # Link magnitude to the origin
        self.magnitude.setCreationInfo(self.create_creation_info())

    def create_creation_info(self):
        """Create a CreationInfo object."""
        cinfo = sc_dm.CreationInfo()
        cinfo.setAgencyID("pyfinder")  
        cinfo.setAuthor("pyfinder@dtgeo")
        return cinfo

    def add_rupture_polygon(self, polygon_coords):
        """Attach rupture polygon information as a comment to the event."""
        return
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
        amplitude.setUnit("cm/s^2")
        amplitude.setTimeWindow(sc_dm.TimeWindow(sc_core.Time.FromString(pga_time, "%Y-%m-%dT%H:%M:%S.%fZ")))
        
        # Create the WaveformStreamID with positional arguments
        network_code, station_code = station_id.split('.')
        amplitude.setWaveformID(sc_dm.WaveformStreamID(network_code, station_code, "", channel_code, ""))

        # Set the web service name in MethodID
        amplitude.setMethodID(web_service_name)

        self.amplitudes.append(amplitude)

    def add_web_service_comment(self, obj, web_service_name):
        """Add a unique comment to the Origin or Event object."""
        return
        comment_text = f"Queried from: {web_service_name}"
        
        # Check if the same comment already exists for the object
        # to skip the duplicates
        if any(obj.comment(i).text() == comment_text for i in range(obj.commentCount())):
            return


        # Create a new comment
        comment = sc_dm.Comment()
        comment.setText(comment_text)
        
        # Assign a unique public ID to the comment
        # comment.setPublicID(f"smi:finder/{self.event_id}/comment/{web_service_name}")

        # Attach the comment to the origin or event
        obj.add(comment)

    def notify_messaging_system(self):
        """Send the event, origin, and amplitude data through the messaging system."""
        if not self.connection():
            sc_logging.error("Messaging connection not established")
            # raise RuntimeError("Messaging connection not established")

        # Create a NotifierMessage
        notifier_msg = sc_dm.NotifierMessage()

        # Enable notifiers
        sc_dm.Notifier.Enable()

        # Attach the notifiers for each object (Origin, Magnitude, Event, Amplitudes)
        notifier_msg.attach(sc_dm.Notifier.Create(self.origin, sc_dm.OP_ADD, self.origin))
        notifier_msg.attach(sc_dm.Notifier.Create(self.magnitude, sc_dm.OP_ADD, self.magnitude))
        notifier_msg.attach(sc_dm.Notifier.Create(self.event, sc_dm.OP_ADD, self.event))

        for amplitude in self.amplitudes:
            notifier_msg.attach(sc_dm.Notifier.Create(self.origin, sc_dm.OP_ADD, amplitude))

        # Send the notifier message to the appropriate messaging groups
        if not self.connection().send("LOCATION", notifier_msg):
            sc_logging.error("Failed to send the notifier message to LOCATION group")
            # raise RuntimeError("Failed to send the notifier message to LOCATION group")

        if not self.connection().send("MAGNITUDE", notifier_msg):
            sc_logging.error("Failed to send the notifier message to MAGNITUDE group")
            # raise RuntimeError("Failed to send the notifier message to MAGNITUDE group")

        if not self.connection().send("EVENT", notifier_msg):
            sc_logging.error("Failed to send the notifier message to EVENT group")
            # raise RuntimeError("Failed to send the notifier message to EVENT group")

        sc_logging.info("Notifier message sent successfully to LOCATION, MAGNITUDE, and EVENT groups")


    def calculate_magnitude_from_pga(self):
        """Calculate magnitude from PGA (stub function)."""
        return 5.5  # Example value


if __name__ == "__main__":
    app = FinderToSeiscomp("finder_event_3")
    app()

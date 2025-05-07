import os
import sys
# Add the parent directory to the system path
# to import the necessary modules
if not os.path.abspath("../") in sys.path:
    sys.path.insert(0, os.path.abspath("../"))

import threading
import time
from datetime import timezone, timedelta
from datetime import datetime
from services.database import ThreadSafeDB
from services.scheduler import FollowUpScheduler
from services.eventtracker import EventTracker

class EventAlertWSPlaybackManager:
    """
    Class to manage the playback of EMSC event alerts for testing purposes.
    This class replaces the real-time event alerts with a pre-defined list of events.
    The whole processing chain for the parametric dataset workflow is executed
    normally, so the RRSM and ESM web services will be actually called. 
    """
    def __init__(self, event_list, event_tracker, speedup_factor=1.0, default_services=None):
        """
        event_list: List of events to be played back, in the same JSON structure as the alerts from EMSC
        event_tracker: Instance of ThreadSafeDB
        scheduler: Instance of FollowUpScheduler
        speedup_factor: Speed multiplier for playback
        default_services: Default services if event doesn't specify
        """
        self.event_list = sorted(event_list, key=lambda e: e['time'])
        self.event_tracker = event_tracker
        self.speedup_factor = speedup_factor
        self.default_services = default_services or ["RRSM", "ESM"]  
        self.index = 0
        self.running = False
        self._thread = None
        self._lock = threading.Lock()

    def start_auto(self):
        """Start automatic playback."""
        if self.running:
            print("[EMSC Event Alert Playback] Already running.")
            return

        self.running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        print("[EMSC Event Alert Playback] Started automatic playback.")

    def pause(self):
        """Pause automatic playback."""
        if not self.running:
            print("[EMSC Event Alert Playback] Already paused.")
            return

        self.running = False
        if self._thread:
            self._thread.join()
        print("[EMSC Event Alert Playback] Paused.")

    def inject_next_event(self):
        """Manually inject the next event."""
        with self._lock:
            if self.index >= len(self.event_list):
                print("[EMSC Event Alert Playback] All events have been injected.")
                return

            event = self.event_list[self.index]
            self.index += 1

        print(f"[EMSC Event Alert Playback] Injecting event {event['unid']} manually at {datetime.now().isoformat()}")
        self._inject_event(event)

    def _run(self):
        """Internal thread loop for automatic playback."""
        while self.running and self.index < len(self.event_list):
            with self._lock:
                event = self.event_list[self.index]
                self.index += 1

            print(f"[EMSC Event Alert Playback] Auto-injecting event {event['unid']} at {datetime.now().isoformat()}")
            self._inject_event(event)

            if self.index < len(self.event_list):
                next_event = self.event_list[self.index]
                sleep_seconds = (datetime.fromisoformat(next_event['time']) - datetime.fromisoformat(event['time'])).total_seconds()
                sleep_seconds /= self.speedup_factor
                if sleep_seconds > 0:
                    time.sleep(min(sleep_seconds, 60))  # Sleep max 60 sec between events even if huge gaps
        # Stay alive after injecting all events
        print("[EMSC Event Alert Playback] All events injected. Waiting for external termination...")
        try:
            while self.running:
                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            self.running = False

    def _inject_event(self, event):
        """Internal helper to inject an event into system."""
        scaled_expiration = max(0.01, 5.0 / self.speedup_factor)  
       
        self.event_tracker.register_event(
            event_id=event['unid'], 
            services=self.default_services, 
            expiration_days=scaled_expiration,
            last_update_time=event['lastupdate'],
            origin_time=event['time'],
            )
        
    def reset(self):
        """Reset to beginning."""
        self.pause()
        with self._lock:
            self.index = 0


if __name__ == "__main__":
    def handle_shutdown(signum, frame):
        print("\n[Main] Interrupt received. Shutting down...")
        playback.pause()
        scheduler.shutdown()
        sys.exit(0)
    

    # Example event list for playback: Kahramanmaras, Turkey 2023
    # and Norcia, Italy 2016. This is the JSON structure used by EMSC
    # and the one that will be used in the playback.
    base_time = datetime.now(timezone.utc)
    event_list = [
        {'source_id': '00000001', 
         'source_catalog': 'EMSC-RTS', 
         # 'lastupdate': '2023-02-06T01:17:36Z', 
         # 'time': '2023-02-06T01:17:36Z', 
         'time': (base_time + timedelta(seconds=0)).isoformat(),
         'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
         'flynn_region': 'EASTERN TURKEY', 
         'lat':37.17, 'lon':37.08, 'depth':20.0,
         'evtype': 'ke', 'auth': 'SCSN', 'mag': 7.7, 'magtype': 'Mw', 
         'unid': '20230206_0000008', 
         'action': 'create'
         },
        # {'source_id': '00000002',
        #  'source_catalog': 'EMSC-RTS', 
        #  # 'lastupdate': '2016-10-30T06:40:18Z', 
        #  # 'time': '2016-10-30T06:40:18Z', 
        #  'time': (base_time + timedelta(seconds=60)).isoformat(),
        #  'lastupdate': (base_time + timedelta(seconds=60)).isoformat(),
        #  'flynn_region': 'ITALY', 
        #  'lat':42.83794, 'lon':13.12324, 'depth':6.2,
        #  'evtype': 'ke', 'auth': 'SCSN', 'mag': 6.6, 'magtype': 'Mw', 
        #  'unid': '20161030_0000029', 
        #  'action': 'update'
        # }
    ]

    # Start with a clean database
    for file in ["test_playback.db", "test_playback.db-shm", "test_playback.db-wal"]:
        if os.path.exists(file):
            os.remove(file)
    tracker = EventTracker("test_playback.db")

    
    # Initialize the scheduler with the database instance
    scheduler = FollowUpScheduler(tracker=tracker)

    # Start the scheduler in a separate thread. This is how the implementation
    # is done in the real-time system.
    def scheduler_loop():
        scheduler.run_forever()
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()

    # Playback manager instance
    playback = EventAlertWSPlaybackManager(event_list, tracker, speedup_factor=1.0, 
                                           default_services=["RRSM"])

    # Pause when you want
    time.sleep(5)
    playback.pause()

    # Inject manually
    playback.inject_next_event()

    # Resume auto
    playback.start_auto()

    
    # Block main thread
    print("[Main] Running playback. Press Ctrl+C to exit.")
    try:
        while scheduler_thread.is_alive():
            scheduler_thread.join(timeout=1)
    except (KeyboardInterrupt, SystemExit):
        handle_shutdown(None, None)

    
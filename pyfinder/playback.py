import os
import sys
import argparse
import json
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse as parse_normalized_iso8601
# Add the parent directory to the system path
# to import the necessary modules
if not os.path.abspath("../") in sys.path:
    sys.path.insert(0, os.path.abspath("../"))

import threading
import time
from time import sleep
from services.database import ThreadSafeDB
from services.scheduler import FollowUpScheduler
from services.eventtracker import EventTracker
from services.querypolicy import RRSMQueryPolicy


def generate_event_list():
    """
    Generate a list of events for testing purposes.
    """
    base_time = datetime.now(timezone.utc)
    return [
        {
            'source_id': '00000001', 'source_catalog': 'EMSC-RTS',
            'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
            'time': (base_time + timedelta(seconds=0)).isoformat(),
            'flynn_region': 'NORCIA, ITALY',
            'lat': 42.84, 'lon': 13.11, 'depth': 10.0,
            'evtype': 'ke', 'auth': 'SCSN', 'mag': 6.5, 'magtype': 'Mw',
            'unid': '20161030_0000029', 'action': 'create'
        },

        {
            'source_id': '00000002', 'source_catalog': 'EMSC-RTS',
            'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
            'time': (base_time + timedelta(seconds=0)).isoformat(),
            'flynn_region': 'PAZARCIK, TURKEY',
            'lat': 37.17, 'lon': 37.08, 'depth': 20.0,
            'evtype': 'ke', 'auth': 'SCSN', 'mag': 7.8, 'magtype': 'Mw',
            'unid': '20230206_0000008', 'action': 'create'
        },

        {
            'source_id': '00000003', 'source_catalog': 'EMSC-RTS',
            'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
            'time': (base_time + timedelta(seconds=0)).isoformat(),
            'flynn_region': 'ELBISTAN, TURKEY',
            'lat': 38.11, 'lon': 37.24, 'depth': 10.0,
            'evtype': 'ke', 'auth': 'SCSN', 'mag': 7.5, 'magtype': 'Mw',
            'unid': '20230206_0000222', 'action': 'create'
        },

        {
            'source_id': '00000004', 'source_catalog': 'EMSC-RTS',
            'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
            'time': (base_time + timedelta(seconds=0)).isoformat(),
            'flynn_region': 'CRETE, GREECE',
            'lat': 35.72, 'lon': 25.91, 'depth': 53.0,
            'evtype': 'ke', 'auth': 'SCSN', 'mag': 6.2, 'magtype': 'Mw',
            'unid': '20250522_0000028', 'action': 'create'
        },

        {
            'source_id': '00000005', 'source_catalog': 'EMSC-RTS',
            'lastupdate': (base_time + timedelta(seconds=0)).isoformat(),
            'time': (base_time + timedelta(seconds=0)).isoformat(),
            'flynn_region': 'ISTANBUL, TURKEY',
            'lat': 40.887, 'lon': 28.138, 'depth': 12.0,
            'evtype': 'ke', 'auth': 'SCSN', 'mag': 6.2, 'magtype': 'Mw',
            'unid': '20250423_0000104', 'action': 'create'
        }
    ]

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
        
        # Override the event's lastupdate and time to current time
        now = datetime.now(timezone.utc).isoformat()
        event['lastupdate'] = now
        event['time'] = now

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
    parser = argparse.ArgumentParser(description="EMSC Event Alert Playback Tool")
    parser.add_argument("--event-id", type=str, nargs='+', help="Inject one or more specific events by ID.")
    args = parser.parse_args()

    def handle_shutdown(signum, frame):
        print("\n[Main] Interrupt received. Shutting down...")
        playback.pause()
        scheduler.shutdown()
        sys.exit(0)
    

    # The predefined list of events to be played back
    event_list = generate_event_list()
    if args.event_id:
        event_list = [e for e in event_list if e['unid'] in args.event_id]
    # Make sure we have events to play back
    if not event_list:
        print("No events found for the specified IDs. Exiting.")
        sys.exit(1)

    # Start with a clean database
    for file in ["test_playback.db", "test_playback.db-shm", "test_playback.db-wal"]:
        if os.path.exists(file):
            os.remove(file)
    tracker = EventTracker("test_playback.db")

    # Initialize the scheduler with the database instance
    scheduler = FollowUpScheduler(tracker=tracker)

    # Start the scheduler in a separate thread. This is also how the implementation
    # is done in the real-time system.
    def scheduler_loop():
        scheduler.run_forever()
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()

    # Playback manager instance
    playback = EventAlertWSPlaybackManager(
        event_list=event_list, event_tracker=tracker, 
        speedup_factor=1.0, default_services=["RRSM"])

    # Inject events manually with policy and batch register
    

    for event in playback.event_list:
        event_id = event["unid"]
        origin_time = parse_normalized_iso8601(event["time"])
        emsc_alert_json = json.dumps(event)

        # Register event
        tracker.batch_register_from_policy(
            event_id=event_id,
            origin_time=origin_time,
            last_update_time=parse_normalized_iso8601(event["lastupdate"]).isoformat(timespec='seconds'),
            emsc_alert_json=emsc_alert_json,
            policy=RRSMQueryPolicy(), 
        )

        print(f"Injected event {event_id} at {origin_time.isoformat(timespec='microseconds')}")
        sleep(1.5)  # slight delay between injections

    # The following legacy calls are commented out as per instructions
    # playback.start_auto()
    # playback.inject_next_event()

    # Block main thread
    print("[Main] Running playback. Press Ctrl+C to exit.")
    try:
        while scheduler_thread.is_alive():
            scheduler_thread.join(timeout=1)
    except (KeyboardInterrupt, SystemExit):
        handle_shutdown(None, None)
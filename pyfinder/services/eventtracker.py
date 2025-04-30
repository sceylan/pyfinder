from pyfinder.services.database import ThreadSafeDB
from datetime import datetime

class EventTracker:
    def __init__(self, db_path="event_tracker.db"):
        self.db = ThreadSafeDB(db_path)
        self.logger = None

    def set_logger(self, logger):
        """Set a logger for the EventTracker."""
        self.logger = logger

    def register_event(self, event_id, services, origin_time, last_update_time, expiration_days=5):
        """Register a new event for one or more services."""
        self.db.add_event(
            event_id=event_id, 
            services=services, 
            expiration_days=expiration_days,
            origin_time=origin_time,
            last_update_time=last_update_time
            )

    def get_due_events(self, service, limit=10):
        """Fetch events that are due for querying for a given service."""
        return self.db.fetch_due_events(service=service, limit=limit)

    def update_status(self, event_id, service, status, next_minutes=30):
        """Update event status and schedule next query."""
        self.db.update_event_status(event_id, service, status, next_minutes)

    def mark_completed(self, event_id, service):
        """Mark event as completed if data changed; otherwise defer."""
        self.db.mark_event_completed(event_id, service)

    def log_failure(self, event_id, service, error):
        """Log an error for a failed query attempt."""
        self.db.log_query_error(event_id, service, error)

        if self.logger:
            self.logger.error(f"Event {event_id} failed for service {service}: {error}")

    def retry_failures(self, max_retries=5):
        """Retry failed events that haven't exceeded retry limits."""
        self.db.retry_failed_events(max_retries)

    def cleanup_expired(self):
        """Clean up expired events from the database."""
        self.db.cleanup_expired_events()

    def close(self):
        """Close database connection."""
        self.db.close()

    def register_event_after_update(self, event_id, services, new_last_update_time):
        """ Register an event after an update with the new last update time. """
        for service in services:
            old_meta = self.db.get_event_meta(event_id, service)
            if old_meta is None:
                # No previous entry; just create new
                self.db.add_event(event_id, [service], new_last_update_time)
                continue

            # Step 1: Mark old event as completed (updated)
            self.db.mark_event_as_completed_due_to_update(event_id, service)

            # Step 2: Insert new event copying old fields
            with self.db._lock:
                self.db.cursor.execute('''
                INSERT OR REPLACE INTO event_tracker (
                    event_id, service, status, origin_time, last_update_time, last_query_time,
                    next_query_time, retry_count, update_attempt_count, expiration_time,
                    priority, last_error, last_data_hash, last_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_id,
                    service,
                    "Pending",                          # Force reset status
                    old_meta['origin_time'],             # Preserve origin time
                    new_last_update_time,                # Set new EMSC lastupdate
                    old_meta['last_query_time'],          # Preserve query history
                    old_meta['next_query_time'],          # Preserve next scheduled time
                    old_meta['retry_count'],              # Preserve retries
                    old_meta['update_attempt_count'],     # Preserve update attempts
                    old_meta['expiration_time'],          # Preserve expiration
                    1,                                    # Priority (can be tuned)
                    None,                                 # Clear last error
                    None,                                 # Clear last data hash
                    datetime.now().isoformat()            # New last modified
                ))
                self.db.conn.commit()

if __name__ == "__main__":
    tracker = EventTracker()
    tracker.register_event("test_event_001", ["RRSM", "ESM"])
    due = tracker.get_due_events("RRSM")
    print("Due events for RRSM:", due)
    
    sample_data = '{"mag": 5.2, "region": "TEST"}'
    tracker.mark_completed("test_event_001", "RRSM", sample_data)
    
    tracker.log_failure("test_event_001", "ESM", "Simulated error")
    tracker.retry_failures()
    tracker.cleanup_expired()
    tracker.close()
# -*- coding: utf-8 -*-
""" 
Module for the EventTracker class for encapsulating the database operations for 
event update status tracking and management. This class serves as a wrapper around
the ThreadSafeDB class to provide a relatively higher-level interface for managing 
events, including registering, updating, and querying.
"""
from pyfinder.services.database import ThreadSafeDB
from datetime import datetime
import logging
from utils.customlogger import file_logger

class EventTracker:
    def __init__(self, db_path="event_tracker.db", logger=None):
        self.db = ThreadSafeDB(db_path)
        logger = logger or logging.getLogger("pyfinder")
        self.set_logger(logger)

    def set_logger(self, logger=None):
        """Set a logger for the EventTracker."""
        if logger is None:
            self.logger = file_logger(
                module_name="EventTracker",
                log_file="eventtracker.log",
                rotate=True,
                overwrite=False,
                level=logging.DEBUG
            )
        else:
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

        # Ensure logger fallback if not already set
        if self.logger is None:
            import utils.customlogger as customlogger
            self.logger = customlogger.file_logger(
                module_name="EventTracker",
                log_file="eventtracker.log",
                rotate=True,
                overwrite=False,
                level=logging.DEBUG
            )
        # self.logger.error(f"Event {event_id} failed for service {service}: {error}")

    def retry_failures(self, max_retries=5):
        """Retry failed events that haven't exceeded retry limits."""
        self.db.retry_failed_events(max_retries)

    def cleanup_expired(self):
        """Clean up expired events from the database."""
        self.db.cleanup_expired_events()

    def close(self):
        """Close database connection."""
        self.db.close()

    def register_event_after_update(self, event_id, services, new_last_update_time, origin_time=None,
                                    expiration_days=5):
        """ 
        Register an event after an update with the new last update time. 

        The database supports multiple services ('service' field) for the same event ID 
        to follow future updates. This provides some level of flexibility for manipulating
        the update follow-up processing chain. The 'status' field is set to "Pending"
        by default to force an update, and its value is hard coded.
        """
        for service in services:
            old_meta = self.db.get_event_meta(event_id, service)
            if old_meta is None:
                # No previous entry; just create new
                self.db.add_event(event_id, [service], origin_time, 
                                  new_last_update_time, expiration_days)
                continue

            # Step 1: Mark old event as completed (updated)
            self.db.mark_event_completed(event_id, service)

            # Step 2: Insert new event copying old fields
            with self.db._lock:
                self.db.cursor.execute('''
                INSERT OR REPLACE INTO event_tracker (
                    event_id, service, status, origin_time, last_update_time, last_query_time,
                    next_query_time, retry_count, update_attempt_count, expiration_time,
                    priority, last_error, last_data_hash, last_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_id,                             # Event ID
                    service,                              # Service name (e.g., RRSM, ESM)
                    "Pending",                            # Force reset status
                    old_meta['origin_time'],              # Preserve origin time
                    new_last_update_time,                 # Set new EMSC lastupdate
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

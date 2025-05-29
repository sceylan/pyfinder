# -*- coding: utf-8 -*-
""" 
Module for the EventTracker class for encapsulating the database operations for 
event update status tracking and management. This class serves as a wrapper around
the ThreadSafeDB class to provide a relatively higher-level interface for managing 
events, including registering, updating, and querying.
"""

from pyfinder.services.database import ThreadSafeDB
from datetime import datetime, timedelta, timezone
import logging
from utils.customlogger import file_logger
from utils.timeutils import parse_normalized_iso8601


class EventTracker:
    class Field:
        event_id = "event_id"
        service = "service"
        status = "status"
        origin_time = "origin_time"
        last_update_time = "last_update_time"
        last_query_time = "last_query_time"
        next_query_time = "next_query_time"
        current_delay_time = "current_delay_time"
        next_delay_time = "next_delay_time"
        retry_count = "retry_count"
        expiration_time = "expiration_time"
        priority = "priority"
        last_error = "last_error"
        last_data_hash = "last_data_hash"
        last_data_snapshot = "last_data_snapshot"
        emsc_alert_json = "emsc_alert_json"
        last_modified = "last_modified"
        
    def __init__(self, db_path="event_update_follow_up.db", logger=None):
        self.db = ThreadSafeDB(db_path)
        logger = logger or logging.getLogger("pyfinder")
        self.set_logger(logger)
        # Attach logger to DB for warnings (conflict inserts)
        self.db.set_logger(self.logger)

    def set_logger(self, logger=None):
        """Set a logger for the EventTracker and pass it to DB."""
        self.logger = logger
        if hasattr(self, "db"):
            self.db.set_logger(logger)

    def initialize_event(self, event_id, services, origin_time, last_update_time, expiration_days=5):
        """Initialize a new event for one or more services."""
        self.db.add_event(
            event_id=event_id, 
            services=services, 
            expiration_days=expiration_days,
            origin_time=origin_time,
            last_update_time=last_update_time
            )

    def get_due_events(self, service):
        """Fetch events that are due for querying for a given service."""
        return self.db.fetch_due_events(service=service)

    def mark_completed(self, event_id, service):
        """Mark event as completed if data changed; otherwise defer."""
        self.db.mark_event_completed(event_id, service)

    def cleanup_expired(self):
        """Clean up expired events from the database."""
        self.db.cleanup_expired_events()

    def close(self):
        """Close database connection."""
        self.db.close()

    def refresh_after_emsc_alert(
            self, event_id, services, new_last_update_time, origin_time=None,
            expiration_days=5):
        """ 
        Update an existing event after an EMSC alert update.

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
            self.db.upsert_event_state(
                event_id,
                service,
                **{
                    self.Field.status: "Pending",
                    self.Field.origin_time: old_meta[self.Field.origin_time],
                    self.Field.last_update_time: new_last_update_time,
                    self.Field.last_query_time: old_meta[self.Field.last_query_time],
                    self.Field.next_query_time: old_meta[self.Field.next_query_time],
                    self.Field.retry_count: old_meta[self.Field.retry_count],
                    self.Field.expiration_time: old_meta[self.Field.expiration_time],
                    self.Field.priority: 1,
                    self.Field.last_error: None,
                    self.Field.last_data_hash: None,
                    self.Field.last_modified: datetime.now(timezone.utc).isoformat(timespec='seconds')
                }
            )

    def _update_event_fields(self, event_id, service, **fields):
        """Update selected fields for an event (status, next_query_time, etc.)."""
        self.db._update_event_fields(event_id, service, **fields)

    def get_all_pending_events(self):
        """Retrieve all pending or failed events across all services."""
        return self.db.get_all_pending_events()

    def get_event_meta(self, event_id, service):
        """Retrieve full metadata for a specific event and service."""
        return self.db.get_event_meta(event_id, service)

    def defer_event(self, event_id, service, minutes=10):
        """Postpone the next query time by N minutes."""
        meta = self.get_event_meta(event_id, service)
        if not meta or not meta.get(self.Field.next_query_time):
            return
        current_time = parse_normalized_iso8601(meta[self.Field.next_query_time])
        new_time = current_time + timedelta(minutes=minutes)
        self._update_event_fields(event_id, service, **{
            self.Field.next_query_time: new_time.isoformat(timespec='microseconds')
        })

    def mark_failed(self, event_id, service, error_message):
        """Mark an event as failed and log the error message."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._update_event_fields(event_id, service, **{
            self.Field.status: "Failed",
            self.Field.last_error: error_message,
            self.Field.last_query_time: now
        })

    def increment_retry_count(self, event_id, service):
        """Increment the retry count for a given event and service."""
        meta = self.get_event_meta(event_id, service)
        if not meta:
            return
        retry = (meta.get(self.Field.retry_count) or 0) + 1
        self._update_event_fields(event_id, service, **{
            self.Field.retry_count: retry
        })

    def query_by_priority(self, min_priority=1):
        """Get events with priority greater than or equal to a given value."""
        return self.db.query_by_priority(min_priority)
        
    def register_update_schedule(
            self, event_id, service, origin_time, last_update_time,
            current_delay_time=None, next_delay_time=None,
            next_query_time=None, emsc_alert_json=None, expiration_days=5, **kwargs):
        """Schedule or update a service update for a specific event."""
        expiration_time = (datetime.now(timezone.utc) + timedelta(days=expiration_days)).isoformat(timespec='seconds')
        self.db.upsert_event_state(
            event_id,
            service,
            **{
                self.Field.status: "Pending",
                self.Field.origin_time: origin_time,
                self.Field.last_update_time: last_update_time,
                self.Field.next_query_time: next_query_time,
                self.Field.current_delay_time: current_delay_time,
                self.Field.next_delay_time: next_delay_time,
                self.Field.emsc_alert_json: emsc_alert_json,
                self.Field.expiration_time: expiration_time,
                **kwargs,
            }
        )

    def batch_register_from_policy(
        self, event_id, policy, origin_time, last_update_time,
        emsc_alert_json=None, expiration_days=5, **kwargs):
        """
        Register multiple scheduled service updates using a policy instance.

        The policy instance must define:
        - policy.service_name (str)
        - policy.schedule_delays (List[float]) in minutes

        Each delay will create a separate row entry with a calculated next_query_time.
        """
        now = datetime.now(timezone.utc)
        delays = policy.QUERY_SCHEDULE_MINUTES
        for i, delay in enumerate(delays):
            print(f"Registering event {event_id} for service {policy.service_name} with delay {delay} minutes")
            
            next_delay = delays[i + 1] if i + 1 < len(delays) else None
            next_query_time = (now + timedelta(minutes=delay)).isoformat(timespec='seconds')
            self.register_update_schedule(
                event_id=event_id,
                service=policy.service_name,
                origin_time=origin_time,
                last_update_time=last_update_time,
                current_delay_time=delay,
                next_delay_time=next_delay,
                next_query_time=next_query_time,
                emsc_alert_json=emsc_alert_json,
                expiration_days=expiration_days,
                **kwargs
            )
    
    def refresh_metadata_after_emsc_update(
        self, event_id, service, new_last_update_time,
        origin_time=None, emsc_alert_json=None
    ):
        """Update EMSC-related metadata without altering the schedule or retry status."""
        fields_to_update = {
            self.Field.last_update_time: new_last_update_time,
            self.Field.last_modified: datetime.now(timezone.utc).isoformat(timespec='seconds'),
        }
        if origin_time:
            fields_to_update[self.Field.origin_time] = origin_time
        if emsc_alert_json:
            fields_to_update[self.Field.emsc_alert_json] = emsc_alert_json

        self._update_event_fields(event_id, service, **fields_to_update)
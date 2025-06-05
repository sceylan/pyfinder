# -*- coding: utf-8 -*-
""" 
Module for the EventTracker class for encapsulating the database operations for 
event update status tracking and management. This class serves as a wrapper around
the ThreadSafeDB class to provide a relatively higher-level interface for managing 
events, including registering, updating, and querying.
"""

from pyfinder.services.database import ThreadSafeDB
from pyfinder.services.database import (
    STATUS_PENDING,
    STATUS_PROCESSING,
    STATUS_COMPLETED,
    STATUS_INCOMPLETE
)
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
        region = "region"
        
    def __init__(self, db_path="event_update_follow_up.db", logger=None):
        self._db = ThreadSafeDB(db_path)
        logger = logger or logging.getLogger("pyfinder")

    def set_logger(self, logger):
        """Set a custom logger for the EventTracker."""
        if not isinstance(logger, logging.Logger):
            raise ValueError("Logger must be an instance of logging.Logger")
        self._db.logger = logger
        self._db.set_logger(logger)
        logger.info("EventTracker logger set successfully.")
        
    def initialize_event(self, event_id, services, origin_time, last_update_time, expiration_days=5):
        """Initialize a new event for one or more services."""
        self._db.add_event(
            event_id=event_id, 
            services=services, 
            expiration_days=expiration_days,
            origin_time=origin_time,
            last_update_time=last_update_time
            )

    def get_due_events(self, service):
        """Fetch events that are due for querying for a given service."""
        return self._db.fetch_due_events(service=service)

    def mark_completed(self, event_id, service, current_delay_time):
        """Mark event as completed with timestamp."""
        self._db.mark_event_completed(event_id, service, current_delay_time)
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._db_update_event_fields(event_id, service, current_delay_time, **{
            self.Field.last_query_time: now
        })

    def mark_as_processing(self, event_id, service, current_delay_time):
        """Mark an event as currently being processed."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._db_update_event_fields(event_id, service, current_delay_time, **{
            self.Field.status: STATUS_PROCESSING,
            self.Field.last_query_time: now
        })

    def cleanup_expired(self):
        """Clean up expired events from the database."""
        self._db.cleanup_expired_events()

    def close(self):
        """Close database connection."""
        self._db.close()

    def _db_update_event_fields(self, event_id, service, current_delay_time, **fields):
        """Update selected fields for an event (status, next_query_time, etc.)."""
        self._db._update_event_fields(event_id, service, current_delay_time, **fields)

    def get_all_pending_events(self):
        """Retrieve all pending or failed events across all services."""
        return self._db.get_all_pending_events()

    def get_event_meta(self, event_id, service, current_delay_time):
        """Retrieve full metadata for a specific event and service."""
        meta = self._db.get_event_meta(event_id, service, current_delay_time)
        if meta:
            try:
                import json
                alert_json = meta.get(self.Field.emsc_alert_json)
                if alert_json:
                    parsed = json.loads(alert_json)
                    meta[self.Field.region] = str(parsed.get("flynn_region")) if "flynn_region" in parsed else None
            except Exception:
                meta[self.Field.region] = None
        return meta

    def mark_failed(self, event_id, service, current_delay_time, error_message):
        """Mark an event as failed and log the error message."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._db_update_event_fields(event_id, service, current_delay_time, **{
            self.Field.status: STATUS_INCOMPLETE,
            self.Field.last_error: error_message,
            self.Field.last_query_time: now
        })

    def increment_retry_count(self, event_id, service, current_delay_time):
        """Increment the retry count for a given event and service."""
        meta = self.get_event_meta(event_id, service, current_delay_time)
        if not meta:
            return
        retry = (meta.get(self.Field.retry_count) or 0) + 1
        self._db_update_event_fields(event_id, service, current_delay_time, **{
            self.Field.retry_count: retry
        })

    def query_by_priority(self, min_priority=1):
        """Get events with priority greater than or equal to a given value."""
        return self._db.query_by_priority(min_priority)
        
    def register_new_schedule(
            self, event_id, service, origin_time, last_update_time,
            current_delay_time=None, next_delay_time=None,
            next_query_time=None, emsc_alert_json=None, expiration_days=5, **kwargs):
        """
        Register a new scheduled service update for a specific event.

        This method will attempt to insert a new row. If the row already exists,
        it will raise an exception and will NOT fallback to updating.
        """
        expiration_time = (datetime.now(timezone.utc) + timedelta(days=expiration_days)).isoformat(timespec='seconds')
        fields = {
            self.Field.status: STATUS_PENDING,
            self.Field.origin_time: origin_time,
            self.Field.last_update_time: last_update_time,
            self.Field.next_query_time: next_query_time,
            self.Field.current_delay_time: current_delay_time,
            self.Field.next_delay_time: next_delay_time,
            self.Field.emsc_alert_json: emsc_alert_json,
            self.Field.expiration_time: expiration_time,
            **kwargs,
        }
        self._db.add_event(event_id, [service], **fields)

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
            self.register_new_schedule(
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
        self, event_id, service, new_last_update_time, origin_time=None, emsc_alert_json=None
    ):
        """
        Update EMSC metadata for all active delay stages of an event (same event_id + service).
        """
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        fields_to_update = {
            self.Field.last_update_time: new_last_update_time,
            self.Field.last_modified: now,
        }
        if origin_time:
            fields_to_update[self.Field.origin_time] = origin_time
        if emsc_alert_json:
            fields_to_update[self.Field.emsc_alert_json] = emsc_alert_json

        all_rows = self.get_all_pending_events()
        for meta in all_rows:
            if (
                meta[self.Field.event_id] == event_id and
                meta[self.Field.service] == service
            ):
                self._db_update_event_fields(
                    event_id=event_id,
                    service=service,
                    current_delay_time=meta[self.Field.current_delay_time],
                    **fields_to_update
                )

        
    def defer_event(self, event_id, service, current_delay_time, minutes=10):
        """Postpone the next query time by N minutes for a specific event and service."""
        meta = self.get_event_meta(event_id, service, current_delay_time)
        if not meta or not meta.get(self.Field.next_query_time):
            return  # Nothing to defer

        current_time = parse_normalized_iso8601(meta[self.Field.next_query_time])
        new_time = current_time + timedelta(minutes=minutes)

        self._db_update_event_fields(event_id, service, current_delay_time, **{
            self.Field.next_query_time: new_time.isoformat(timespec='seconds')
        })
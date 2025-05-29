# -*- coding: utf-8 -*-
# !/usr/bin/env python
""" 
Database utility for tracking events and their query status. This module normally 
should not be used directly, but rather through the services.eventtracker.EventTracker 
class, which provides a higher-level interface for database operations related to event 
updates and follow-ups.
"""

import sqlite3
import threading
import hashlib
from datetime import datetime, timedelta, timezone
from utils.timeutils import parse_normalized_iso8601


STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_INCOMPLETE = "incomplete"


class ThreadSafeDB:
    _lock = threading.Lock()

    def __init__(self, db_path="event_update_follow_up.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._enable_wal()
        self._create_table()

    def _enable_wal(self):
        """Enable Write-Ahead Logging (WAL) mode for better concurrency."""
        self.cursor.execute('PRAGMA journal_mode=WAL;')

    def _create_table(self):
        """Create the event tracking table if it doesn't exist."""
        with self._lock:
            # All timestamps are stored as UTC ISO 8601 strings
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_tracker (
                event_id TEXT,
                service TEXT,
                status TEXT,
                origin_time TEXT,
                last_update_time TEXT,
                last_query_time TEXT,
                next_query_time TEXT,
                current_delay_time REAL DEFAULT NULL,
                next_delay_time REAL DEFAULT NULL,
                retry_count INTEGER DEFAULT 0,
                expiration_time TEXT,
                priority INTEGER DEFAULT 1,
                last_error TEXT DEFAULT NULL,
                last_data_hash TEXT DEFAULT NULL,
                last_data_snapshot TEXT DEFAULT NULL,
                emsc_alert_json TEXT DEFAULT NULL,
                last_modified TEXT DEFAULT (DATETIME('now')),
                PRIMARY KEY (event_id, service, current_delay_time)
            )
            ''')
            self.conn.commit()

    def calculate_hash(self, data):
        """Calculate a hash of the provided data for change detection."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def add_event(self, event_id, services, origin_time, last_update_time, expiration_days=5,
                  current_delay_time=None, next_delay_time=None, emsc_alert_json=None, 
                  next_query_time=None):
        """Add a new event to the database. Logs a warning if insert fails due to conflict."""
        now = datetime.now(timezone.utc)
        expiration_time = (now + timedelta(days=expiration_days)).isoformat(timespec='seconds')
        with self._lock:
            for service in services:
                try:
                    self.cursor.execute('''
                    INSERT INTO event_tracker (
                        event_id, service, status, origin_time, last_update_time, 
                        last_query_time, next_query_time, retry_count, 
                        expiration_time,
                        current_delay_time, next_delay_time, emsc_alert_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (event_id, service, STATUS_PENDING, origin_time, last_update_time, None, 
                          next_query_time or now.isoformat(timespec='seconds'), 0, expiration_time, 
                          current_delay_time, next_delay_time, emsc_alert_json))
                except sqlite3.IntegrityError:
                    # Conflict (duplicate) occurred; log a warning if logger is available
                    if hasattr(self, "logger") and self.logger:
                        self.logger.warning(
                            f"Suppressed duplicate event insert: event_id={event_id}, service={service}, current_delay_time={current_delay_time}"
                        )
                    else:
                        raise
            self.conn.commit()

    def set_logger(self, logger):
        """Attach a logger instance (used for warnings)."""
        self.logger = logger

    def fetch_due_events(self, service=None):
        """Fetch events that are due for querying, optionally filtered by service."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        query = '''
        SELECT event_id, service, current_delay_time FROM event_tracker 
        WHERE next_query_time <= ? AND status IN (?)
        '''
        params = [now, STATUS_PENDING]
        
        if service:
            query += ' AND service = ?'
            params.append(service)
        query += ' ORDER BY priority DESC, next_query_time'
        
        with self._lock:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()

    def mark_event_completed(self, event_id, service, current_delay_time):
        """Mark an event as completed with timestamp."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._update_event_fields(
            event_id,
            service,
            current_delay_time=current_delay_time,
            status=STATUS_COMPLETED,
            last_query_time=now
        )

    def cleanup_expired_events(self):
        """Remove or mark expired events as inactive."""
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        with self._lock:
            self.cursor.execute('''
            DELETE FROM event_tracker
            WHERE expiration_time <= ?
            ''', (now,))
            self.conn.commit()

    def close(self):
        """Close the database connection."""
        with self._lock:
            self.conn.close()

    def get_event_meta(self, event_id, service, current_delay_time):
        with self._lock:
            self.cursor.execute('''
            SELECT event_id, service, origin_time, last_query_time, next_query_time, status, 
                retry_count, expiration_time,
                current_delay_time, next_delay_time, emsc_alert_json, last_data_snapshot
            FROM event_tracker
            WHERE event_id = ? AND service = ? AND current_delay_time = ?
            ''', (event_id, service, current_delay_time))
            row = self.cursor.fetchone()
            if row:
                keys = ["event_id", "service", "origin_time", "last_query_time", "next_query_time", "status",
                        "retry_count", "expiration_time",
                        "current_delay_time", "next_delay_time", "emsc_alert_json", "last_data_snapshot"]
                return dict(zip(keys, row))
            return None


    def defer_event(self, event_id, service, current_delay_time, minutes=10):
        """Postpone the next query time by N minutes."""
        meta = self.get_event(event_id, service, current_delay_time)
        if not meta or not meta.get("next_query_time"):
            return
        current_time = parse_normalized_iso8601(meta["next_query_time"])
        new_time = current_time + timedelta(minutes=minutes)
        self._update_event_fields(event_id, service, current_delay_time=current_delay_time, next_query_time=new_time.isoformat(timespec='seconds'))

    def query_by_priority(self, min_priority=1):
        """Get events with priority greater than or equal to a given value."""
        with self._lock:
            self.cursor.execute('''
                SELECT event_id, service, priority, next_query_time
                FROM event_tracker
                WHERE priority >= ?
                ORDER BY priority DESC, next_query_time ASC
            ''', (min_priority,))
            return self.cursor.fetchall()

    def _update_event_fields(self, event_id, service, current_delay_time, **kwargs):
        """
        Update specific fields of an event.
        """
        columns = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                columns.append(f"{key} = ?")
                values.append(value)
        if not columns:
            if hasattr(self, "logger") and self.logger:
                self.logger.warning(f"_update_event_fields skipped: no valid fields for event_id={event_id}, service={service}")
            return
        values.extend([event_id, service, current_delay_time])
        with self._lock:
            self.cursor.execute(f'''
                UPDATE event_tracker
                SET {", ".join(columns)}
                WHERE event_id = ? AND service = ? AND current_delay_time = ?
            ''', values)
            self.conn.commit()

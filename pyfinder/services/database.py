# -*- coding: utf-8 -*-
# !/usr/bin/env python
""" Database utility for tracking events and their query status. """

import sqlite3
import threading
import hashlib
from datetime import datetime, timedelta

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
                update_attempt_count INTEGER DEFAULT 0,
                expiration_time TEXT,
                priority INTEGER DEFAULT 1,
                last_error TEXT DEFAULT NULL,
                last_data_hash TEXT DEFAULT NULL,
                last_data_snapshot TEXT DEFAULT NULL,
                emsc_alert_json TEXT DEFAULT NULL,
                last_modified TEXT DEFAULT (DATETIME('now')),
                PRIMARY KEY (event_id, service)
            )
            ''')
            self.conn.commit()

    def calculate_hash(self, data):
        """Calculate a hash of the provided data for change detection."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def add_event(self, event_id, services, origin_time, last_update_time, expiration_days=5,
                  current_delay_time=None, next_delay_time=None, emsc_alert_json=None, 
                  next_query_time=None):
        """Add a new event to the database."""
        now = datetime.now()
        expiration_time = (now + timedelta(days=expiration_days)).isoformat()
        with self._lock:
            for service in services:
                self.cursor.execute('''
                INSERT OR IGNORE INTO event_tracker (
                    event_id, service, status, origin_time, last_update_time, 
                    last_query_time, next_query_time, retry_count, 
                    update_attempt_count, expiration_time,
                    current_delay_time, next_delay_time, emsc_alert_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (event_id, service, "Pending", origin_time, last_update_time, None, 
                      next_query_time or now.isoformat(), 0, 0, expiration_time, 
                      current_delay_time, next_delay_time, emsc_alert_json))
            self.conn.commit()

    def fetch_due_events(self, service=None, limit=10):
        """Fetch events that are due for querying, optionally filtered by service."""
        now = datetime.now().isoformat()
        query = '''SELECT event_id, service FROM event_tracker 
                   WHERE next_query_time <= ? AND status IN ("Pending", "Failed")'''
        params = [now]
        if service:
            query += ' AND service = ?'
            params.append(service)
        query += ' ORDER BY priority DESC, next_query_time ASC LIMIT ?'
        params.append(limit)
        with self._lock:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()

    def _update_event_status_locked(self, event_id, service, status, next_query_time):
        """Update the status of an event and schedule the next query time (requires lock to be held)."""
        now = datetime.now()
        self.cursor.execute('''
            UPDATE event_tracker
            SET status = ?, last_query_time = ?, next_query_time = ?, 
                update_attempt_count = update_attempt_count + 1,
                current_delay_time = NULL, next_delay_time = NULL,
                last_modified = ?
            WHERE event_id = ? AND service = ?
            ''', (status, now.isoformat(), next_query_time, now.isoformat(), event_id, service))
        self.conn.commit()

    def update_event_status(self, event_id, service, status, next_query_time):
        """Public method to update event status with locking."""
        if not self._lock.acquire(timeout=10):  # Timeout to prevent indefinite locking
            raise TimeoutError("Database lock acquisition timed out.")
        try:
            self._update_event_status_locked(event_id, service, status, next_query_time)
        finally:
            self._lock.release()

    
    def mark_event_completed(self, event_id, service):
        """Deprecated: use `upsert_event_state` to mark status."""
        now = datetime.now().isoformat()
        with self._lock:
            self.cursor.execute('''
            UPDATE event_tracker
            SET status = "Completed", last_query_time = ?, last_modified = ?
            WHERE event_id = ? AND service = ?
            ''', (now, now, event_id, service))
            self.conn.commit()

    def retry_failed_events(self, max_retries=5):
        """Deprecated: retry logic should be handled externally."""
        now = datetime.now()
        with self._lock:
            self.cursor.execute('''
            UPDATE event_tracker
            SET status = "Pending", next_query_time = ?, retry_count = retry_count + 1, last_modified = ?
            WHERE status = "Failed" AND retry_count < ?
            ''', (now.isoformat(), now.isoformat(), max_retries))
            self.conn.commit()

    def log_query_error(self, event_id, service, error_message, next_interval_minutes=30):
        """Deprecated: use `upsert_event_state` instead."""
        now = datetime.now()
        next_query_time = (now + timedelta(minutes=next_interval_minutes)).isoformat()
        with self._lock:
            self.cursor.execute('''
            UPDATE event_tracker
            SET status = "Failed", last_error = ?, retry_count = retry_count + 1, 
                current_delay_time = NULL, next_delay_time = NULL,
                last_modified = ?, next_query_time = ?
            WHERE event_id = ? AND service = ?
            ''', (error_message, now.isoformat(), next_query_time, event_id, service))
            self.conn.commit()

    def cleanup_expired_events(self):
        """Remove or mark expired events as inactive."""
        now = datetime.now().isoformat()
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

    def get_event_meta(self, event_id, service):
        with self._lock:
            self.cursor.execute('''
            SELECT event_id, service, origin_time, last_query_time, next_query_time, status, 
                retry_count, update_attempt_count, expiration_time,
                current_delay_time, next_delay_time, emsc_alert_json, last_data_snapshot
            FROM event_tracker
            WHERE event_id = ? AND service = ?
            ''', (event_id, service))
            row = self.cursor.fetchone()
            if row:
                keys = ["event_id", "service", "origin_time", "last_query_time", "next_query_time", "status",
                        "retry_count", "update_attempt_count", "expiration_time",
                        "current_delay_time", "next_delay_time", "emsc_alert_json", "last_data_snapshot"]
                return dict(zip(keys, row))
            return None

    def upsert_event_state(self, event_id, service, **kwargs):
        """
        Insert or update a full or partial event state.
        Only updates fields that are explicitly provided.
        """
        now = datetime.now().isoformat()
        kwargs["last_modified"] = now

        columns = ["event_id", "service"]
        values = [event_id, service]
        update_clause = []

        for key, value in kwargs.items():
            columns.append(key)
            values.append(value)
            update_clause.append(f"{key}=excluded.{key}")

        with self._lock:
            self.cursor.execute(f'''
                INSERT INTO event_tracker ({", ".join(columns)})
                VALUES ({", ".join("?" for _ in columns)})
                ON CONFLICT(event_id, service) DO UPDATE SET
                    {", ".join(update_clause)}
            ''', values)
            self.conn.commit()

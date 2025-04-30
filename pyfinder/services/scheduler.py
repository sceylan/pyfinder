# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
import logging
from concurrent.futures import ThreadPoolExecutor

from pyfinder.findermanager import FinDerManager
from pyfinder.services.eventtracker import EventTracker
from pyfinder.services.querypolicy import SERVICE_POLICIES
from pyfinder.utils.customlogger import FileLoggingFormatter



class FollowUpScheduler:
    """
    FollowUpScheduler is responsible for managing the scheduling of follow-up queries.
    It uses a thread pool to handle multiple events concurrently and logs the process.
    The scheduler checks for due events and processes them according to the defined 
    policies via dedicated policy instances in the SERVICE_POLICIES.
    """
    def __init__(self, tracker: EventTracker):
        self.tracker = tracker
        self.logger = self._setup_file_logger()
        self.tracker.set_logger(self.logger)
        self.logger.info("FollowUpScheduler initialized.")

        # Thread pool with up to 10 workers
        self.executor = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def _setup_file_logger(rotate=True):
        """ Set up a file logger for the FollowUpScheduler."""
        logger = logging.getLogger("FollowUpScheduler")
        logger.setLevel(logging.NOTSET)
        logger.propagate = False

        if logger.handlers:
            return logger

        formatter = FileLoggingFormatter()
        mode = "a"

        if rotate:
            try:
                fh = logging.handlers.RotatingFileHandler(
                    "followupscheduler.log", maxBytes=1000000, backupCount=7, encoding='utf-8', mode=mode
                )
            except Exception:
                fh = logging.FileHandler(__name__, mode=mode, encoding='utf-8')
        else:
            fh = logging.FileHandler(__name__, mode=mode, encoding='utf-8')

        fh.setLevel(logging.NOTSET)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger

    def _handle_event(self, event_id, service, event_meta, policy):
        """ Method to handle the event alert. Triggered by the ThreadPoolExecutor."""
        try:
            delay = policy.get_next_query_delay_minutes(event_meta)
            if delay is None:
                self.tracker.mark_completed(event_id, service)
                self.logger.info(f"Event {event_id}: Completed. End of life cycle for {service}, no further queries.")
                return

            # Run FinDerManager to process the event
            self.logger.info(f"Running FinDerManager for event {event_id}.")

            finder_options = {
                "verbosity": "INFO",
                "log_file": None,
                "with_seiscomp": True,
                "event_id": event_id,
                "test": False,
                "use_library": False
            }
            # Join all fields as command line arguments
            finder_options['command_line_args'] = " ".join(
                [f"--{k}={v}" for k, v in finder_options.items() if k != "command_line_args"]
            )
            finder_manager = FinDerManager(options=finder_options)
            finder_solution = finder_manager.run(event_id=event_id)
            
            success = True if finder_solution is not None else False
            self.logger.info(f"FinDerManager run completed for event {event_id} with this outcome: {success}.")
            
            if success:
                if policy.is_terminal(event_meta):
                    self.tracker.mark_completed(event_id, service)
                    self.logger.info(f"Event {event_id} completed for service {service}.")
                else:
                    self.tracker.update_status(event_id, service, "Pending", next_minutes=delay)
                    due_time = datetime.now(timezone.utc) + timedelta(minutes=delay)
                    self.logger.info(f"Event {event_id} scheduled for next query in {delay} minutes at {due_time}.")
            else:
                if policy.should_retry_on_failure(event_meta):
                    self.tracker.log_failure(event_id, service, "FinDer run failed")
                    self.logger.error(f"FinDer run failed for event {event_id} and service {service}.")
                else:
                    self.tracker.mark_completed(event_id, service)
                    self.logger.error(f"Event {event_id} marked as completed after retry failure for service {service}.")

        except Exception as e:
            self.logger.error(f"Error processing event {event_id} for service {service}: {e}")
            if policy.should_retry_on_failure(event_meta):
                self.tracker.log_failure(event_id, service, str(e))
            else:
                self.tracker.mark_completed(event_id, service)

    def shutdown(self):
        """ Shutdown the FollowUpScheduler and clean up resources. """
        self.logger.info("Shutting down FollowUpScheduler.")

        # Close the database connection
        self.tracker.close()

        # Shutdown the thread pool executor
        self.logger.info("Shutting down thread pool executor.")
        self.executor.shutdown(wait=False)

        self.logger.info("FollowUpScheduler shutdown complete.")

    def run_once(self):
        """ Run the scheduler once to check for due events and process them. """
        due_events = self.tracker.get_due_events(service=None)

        if not due_events:
            return

        self.logger.info(f"Due events fetched: {len(due_events)}")
        self.logger.info(f"Due events: {due_events}")

        for event_id, service in due_events:
            event_meta = self.tracker.db.get_event_meta(event_id, service)
            if not event_meta:
                continue

            policy = SERVICE_POLICIES.get(service)
            self.logger.info(f"Policy for service {service}: {policy}")

            if not policy:
                self.logger.error(f"No policy found for service {service}.")
                continue

            # Submit task to thread pool
            self.executor.submit(self._handle_event, event_id, service, event_meta, policy)

    def run_forever(self, interval_seconds=10):
        """ 
        Run the scheduler in an infinite loop, checking for due events 
        at regular intervals. 
        """
        import time
        self.logger.info(f"Scheduler running every {interval_seconds} seconds.")

        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Scheduler encountered an error: {e}")
            self.shutdown()

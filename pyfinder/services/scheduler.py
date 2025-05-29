# -*- coding: utf-8 -*-
""" 
Main module for the automated FinDer execution via the FollowUpScheduler class, 
which manages the scheduling of follow-up queries. This class manages if another
data update is expected, executes the FinDerManager to process the event, and
handles the results.
"""
from datetime import datetime, timedelta, timezone
import logging
from concurrent.futures import ThreadPoolExecutor

from pyfinder.findermanager import FinDerManager
from pyfinder.services.eventtracker import EventTracker
from pyfinder.services.querypolicy import SERVICE_POLICIES
from pyfinder.utils.customlogger import file_logger


class FollowUpScheduler:
    """
    FollowUpScheduler is responsible for managing the scheduling of follow-up queries.
    It uses a thread pool to handle multiple events concurrently and logs the process.
    The scheduler checks for due events and processes them according to the defined 
    policies via dedicated policy instances in the SERVICE_POLICIES.
    """
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_INCOMPLETE = "incomplete"

    def __init__(self, tracker: EventTracker=None):
        # Create a logger for the FollowUpScheduler and its sub-tasks
        self.logger = self._setup_file_logger()
        self._welcome_message(self.logger)

        # Initialize the EventTracker for managing event updates
        if tracker is None:
            tracker = EventTracker("event_update_follow_up.db")
        self.tracker = tracker
        self.tracker.set_logger(self.logger)
        self.logger.info("EventTracker initialized for the scheduler.")

        # Thread pool with up to 10 workers
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.logger.info("ThreadPoolExecutor initialized for the scheduler.")

        self.logger.info("FollowUpScheduler initialization completed.")
        
    @staticmethod
    def _welcome_message(logger):
        """ Print a welcome message to the console and log it. """
        
        logger.info("=========================================================")
        logger.info(" A new scheduler for event updates is being initialized. ")
        logger.info("... Testing logger functionality ...")
        logger.error("This is an error message for testing purposes.")
        logger.info("This is an info message for testing purposes.")
        logger.ok("This is an ok message for testing purposes.")
        logger.info("---------------------------------------------------------")
        logger.info("BEGIN: Init FollowUpScheduler")

    @staticmethod
    def _setup_file_logger():
        """ Set up a file logger for the FollowUpScheduler."""
        return file_logger(
            module_name="FollowUpScheduler",
            log_file="followupscheduler.log",
            rotate=True,
            overwrite=False
            )

    def _handle_event(self, event_id, service, event_meta, policy):
        """ Method to handle the event alert. Triggered by the ThreadPoolExecutor."""
        try:
            # Check if the event is still valid by asking for the next delay time
            # from the policy object.
            delay = policy.get_next_query_delay_minutes(event_meta)
            
            if delay is None:
                # Event is no longer valid, mark it as completed, and let it run
                # one last time for the final query interval.
                current_delay_time = event_meta.get('current_delay_time', None)
                self.tracker.mark_completed(event_id, service, current_delay_time=current_delay_time)
                self.logger.info(f"Event {event_id}: End of life cycle for {service}, no future queries planned.")

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
            # Join all fields as command line arguments. The command line args are valid 
            # when findermanager is run from the command line. We combine a command line 
            # here anyways for logging purposes only inside the FinDerManager.
            finder_options['command_line_args'] = " ".join(
                [f"--{k}={v}" for k, v in finder_options.items() if k != "command_line_args"]
            )

            # Metadata to keep track of the simulation in between modules
            solution_metadata = {
                "last_query_time": str(event_meta['last_query_time']),
                "minutes_until_next_update": delay,
                "current_delay": policy.get_current_query_delay_minutes(event_meta),
            }

            self.logger.info(f"FinderManager will be triggerred for the current delay for {event_id}: {policy.get_current_query_delay_minutes(event_meta)} minutes.")

            # Create FinDerManager instance and run it
            finder_manager = FinDerManager(options=finder_options, metadata=solution_metadata)
            finder_solution = finder_manager.run(event_id=event_id)
            
            # Check if FinDerManager run was successful
            success = True if finder_solution is not None else False
            self.logger.info(f"FinDerManager run completed for event {event_id} with this outcome: {success}.")
            
            current_delay_time = event_meta.get('current_delay_time', None)

            if success:
                self.tracker.mark_completed(event_id, service, current_delay_time=current_delay_time)
                self.logger.info(f"Event {event_id} marked completed for delay {current_delay_time} minutes for service {service}.")
            
            else:
                # If FinDerManager run failed, check if the event is still valid
                if policy.should_retry_on_failure(event_meta):
                    # If we should retry, log the failure and update the status
                    self.tracker.log_failure(event_id, service, "FinDer run failed", current_delay_time=current_delay_time)
                    self.logger.error(f"FinDer run failed for event {event_id} and service {service}.")
                else:
                    # If we shouldn't retry, mark the event as completed. No further queries are needed.
                    self.tracker.mark_completed(event_id, service, current_delay_time=current_delay_time)
                    self.logger.error(f"Event {event_id} marked as completed after retry failure for service {service}.")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing event {event_id} for service {service}: {e}")
            
            current_delay_time = event_meta.get('current_delay_time', None)
            if policy.should_retry_on_failure(event_meta):
                self.tracker.log_failure(event_id, service, str(e), current_delay_time=current_delay_time)
            else:
                self.tracker.mark_completed(event_id, service, current_delay_time=current_delay_time)

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
        self.logger.info(f"Due events: {[(e[0], e[1]) for e in due_events]}")

        for event_id, service, current_delay_time in due_events:
            # Mark the event as processing so that it is not fecthed again in the next
            # loop after sleep. The actual processing chain takes much longer, and this
            # event will keep queried until the FinDerManager run is finished at every call.
            self.tracker._update_event_fields(event_id, service, current_delay_time, **{
                "status": self.STATUS_PROCESSING,
                "current_delay_time": current_delay_time
            })
            self.logger.info(f"Processing event {event_id} for service {service}.")

            event_meta = self.tracker.db.get_event_meta(event_id, service, current_delay_time)
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

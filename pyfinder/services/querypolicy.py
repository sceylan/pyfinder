# -*- coding: utf-8 -*-
"""
Query policy classes for the pyfinder module which defines the rules for querying
the web services for the parametric datasets to follow any updates at the defined
time intervals. 
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
import math

class AbstractPolicy(ABC):
    @abstractmethod
    def should_query(self, event_meta: dict) -> bool:
        """Return True if the service should be queried now."""
        pass

    @abstractmethod
    def get_next_query_delay_minutes(self, event_meta: dict) -> int:
        """Return how many minutes to wait before the next query."""
        pass

    @abstractmethod
    def is_terminal(self, response: dict) -> bool:
        """Return True if the response indicates querying can stop permanently."""
        pass

    @abstractmethod
    def should_retry_on_failure(self, event_meta: dict) -> bool:
        """Return True if the service should retry after failure."""
        pass


########
# RRSM
########
class RRSMQueryPolicy(AbstractPolicy):
    """
    Query RRSM at the following relative times from origin:
    0, 5, 15, 60, 180, 360, 1440, 2880 minutes
    """
    QUERY_SCHEDULE_MINUTES = [0, 5, 15, 60, 180, 360, 1440, 2880]
    QUERY_SCHEDULE_MINUTES = [0, 1, 2, 3]
    ALLOWED_DRIFT_MINUTES = 2  # allow query within 2 minutes window

    def should_query(self, event_meta):
        """Return True if current time is within an allowed window."""
        origin = datetime.fromisoformat(event_meta["origin_time"])
        now = datetime.now(timezone.utc)
        elapsed = (now - origin).total_seconds() / 60.0  # in minutes
        
        # Something is wrong with the time stamps
        if elapsed < 0:
            return False, "Negative elapsed time"
        
        # Expire if beyond max scheduled time + 15 minutes
        if elapsed > max(self.QUERY_SCHEDULE_MINUTES) + 15:
            return False, "Expired beyond allowed time + drift"

        # Check if the elapsed time is within the allowed drift of any scheduled time
        for scheduled in self.QUERY_SCHEDULE_MINUTES:
            if abs(elapsed - scheduled) <= self.ALLOWED_DRIFT_MINUTES:
                return True, "Within allowed drift"
            
        return False, "Not within allowed drift"

    def get_next_query_delay_minutes(self, event_meta):
        origin = datetime.fromisoformat(event_meta["origin_time"])
        now = datetime.now(timezone.utc)
        elapsed = (now - origin).total_seconds() / 60.0

        for scheduled in self.QUERY_SCHEDULE_MINUTES:
            if elapsed < scheduled:
                delay = math.ceil(scheduled - elapsed)
                return max(1, delay)  # Ensure at least 1 minute
        return None  # fallback

    def is_terminal(self, response):
        """RRSM is considered terminal if more than 2 days + 15 min have passed."""
        origin_str = response.get("origin_time")
        if not origin_str:
            return False

        origin = datetime.fromisoformat(origin_str)
        expiration_delta = timedelta(days=max(self.QUERY_SCHEDULE_MINUTES) / 1440) + timedelta(minutes=15)
        return datetime.now(timezone.utc) > (origin + expiration_delta)

    def should_retry_on_failure(self, event_meta):
        return event_meta.get("retry_count", 0) < 3


########
# ESM: Dummy Policy for ESM
########
class ESMQueryPolicy(AbstractPolicy):
    """
    Query ESM at the following relative times from origin:
    0, 5, 15, 60, 180, 360, 1440, 2880 minutes
    """
    QUERY_SCHEDULE_MINUTES = []
    ALLOWED_DRIFT_MINUTES = 2

    def should_query(self, event_meta):
       return False, "Dummy policy: ESM query not implemented"

    def get_next_query_delay_minutes(self, event_meta):
       pass

    def is_terminal(self, response):
       pass

    def should_retry_on_failure(self, event_meta):
        pass


########
# EMSC: Dummy Policy for now
########
class EMSCQueryPolicy(AbstractPolicy):
    """
    Query ESMC at the following relative times from origin:
    0, 5, 15, 60, 180, 360, 1440, 2880 minutes
    """
    QUERY_SCHEDULE_MINUTES = []
    ALLOWED_DRIFT_MINUTES = 2

    def should_query(self, event_meta):
       return False, "Dummy policy: EMSC query not implemented"

    def get_next_query_delay_minutes(self, event_meta):
       pass

    def is_terminal(self, response):
       pass

    def should_retry_on_failure(self, event_meta):
        pass


########
# Registry
########
SERVICE_POLICIES = {
    "RRSM": RRSMQueryPolicy(),
    "ESM": ESMQueryPolicy(),
    "EMSC": EMSCQueryPolicy(),
}
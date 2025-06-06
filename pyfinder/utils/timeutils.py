# -*- coding: utf-8 -*-
from datetime import datetime, timezone


def parse_normalized_iso8601(timestamp: str) -> datetime:
    """Parses an ISO8601 timestamp string into a naive UTC datetime.
    Handles cases like: '2025-05-28T18:00:04.22Z'
    """
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1]  # Remove 'Z'

    # Split fractional part and pad if necessary
    try:
        if "." in timestamp:
            base, frac = timestamp.split(".")
            frac = (frac + "000000")[:6]  # pad to 6 digits
            timestamp = f"{base}.{frac}"
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except Exception as e:
        raise ValueError(f"Failed to parse ISO8601 string: {timestamp}") from e


def normalize_iso8601(ts: str) -> datetime:
    tz = None
    if ts.endswith("Z"):
        ts = ts[:-1]
        tz = timezone.utc

    if "." in ts:
        date_part, frac = ts.split(".")
        if "+" in frac or "-" in frac:  # timezone present
            frac_part, tz_part = frac[:-6], frac[-6:]
            frac_part = (frac_part + "000000")[:6]
            ts = f"{date_part}.{frac_part}{tz_part}"
        else:
            frac = (frac + "000000")[:6]
            ts = f"{date_part}.{frac}"

    dt = datetime.fromisoformat(ts)
    return dt.replace(tzinfo=tz) if tz else dt
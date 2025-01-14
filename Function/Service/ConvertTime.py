from datetime import datetime, timezone, timedelta

# Bangkok timezone offset
BANGKOK_OFFSET = timedelta(hours=7)

def ts_int10_to_datetime(ts: int) -> datetime:
    """Convert a 10-digit (seconds) timestamp to UTC datetime."""
    return datetime.utcfromtimestamp(ts)

def ts_int13_to_datetime(ts: int) -> datetime:
    """Convert a 13-digit (milliseconds) timestamp to UTC datetime."""
    return datetime.utcfromtimestamp(ts / 1000)

def ts_int10_to_datetime_bangkok(ts: int) -> datetime:
    """Convert a 10-digit (seconds) timestamp to Bangkok datetime."""
    return datetime.utcfromtimestamp(ts) + BANGKOK_OFFSET

def ts_int13_to_datetime_bangkok(ts: int) -> datetime:
    """Convert a 13-digit (milliseconds) timestamp to Bangkok datetime."""
    return datetime.utcfromtimestamp(ts / 1000) + BANGKOK_OFFSET

def datetime_to_ts_int10(dt: datetime) -> int:
    """Convert datetime to a 10-digit (seconds) timestamp."""
    return int(dt.replace(tzinfo=timezone.utc).timestamp())

def datetime_to_ts_int13(dt: datetime) -> int:
    """Convert datetime to a 13-digit (milliseconds) timestamp."""
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

def datetime_to_ts_int10_bangkok(dt: datetime) -> int:
    """Convert Bangkok datetime to a 10-digit (seconds) timestamp."""
    bangkok_dt = dt - BANGKOK_OFFSET
    return int(bangkok_dt.replace(tzinfo=timezone.utc).timestamp())

def datetime_to_ts_int13_bangkok(dt: datetime) -> int:
    """Convert Bangkok datetime to a 13-digit (milliseconds) timestamp."""
    bangkok_dt = dt - BANGKOK_OFFSET
    return int(bangkok_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

if __name__ == "__main__":
    ts_10 = 1734512487  # Example 10-digit timestamp
    ts_13 = 1734512487000  # Example 13-digit timestamp
    dt = datetime(2025, 12, 17, 15, 35)  # Example datetime

    print("10-digit TS to UTC datetime:", ts_int10_to_datetime(ts_10))
    print("13-digit TS to UTC datetime:", ts_int13_to_datetime(ts_13))
    print("10-digit TS to Bangkok datetime:", ts_int10_to_datetime_bangkok(ts_10))
    print("13-digit TS to Bangkok datetime:", ts_int13_to_datetime_bangkok(ts_13))

    print("Datetime to 10-digit TS (UTC):", datetime_to_ts_int10(dt))
    print("Datetime to 13-digit TS (UTC):", datetime_to_ts_int13(dt))
    print("Datetime to 10-digit TS (Bangkok):", datetime_to_ts_int10_bangkok(dt))
    print("Datetime to 13-digit TS (Bangkok):", datetime_to_ts_int13_bangkok(dt))
def to_nanoseconds(times):
    """Converts a time series of seconds to nanoseconds."""
    return [t * 1000000000 for t in times]


def to_microseconds(times):
    """Converts a time series of seconds to microseconds."""
    return [t * 1000000 for t in times]


def to_milliseconds(times):
    """Converts a time series of seconds to milliseconds."""
    return [t * 1000 for t in times]


def to_minutes(times):
    """Converts a time series of seconds to minutes."""
    return [t / 60 for t in times]


def to_hours(times):
    """Converts a time series of seconds to hours."""
    return [t / 3600 for t in times]


def to_days(times):
    """Converts a time series of seconds to days."""
    return [t / 86400 for t in times]

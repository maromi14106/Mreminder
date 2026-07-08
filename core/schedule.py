"""Schedule calculation module."""

from datetime import datetime, timedelta


def truncate_to_minute(dt: datetime) -> datetime:
    """Truncate a datetime to minute precision."""
    return dt.replace(second=0, microsecond=0)


def calculate_initial_next_run(
    now: datetime,
    target_datetime: datetime,
    repeat_type: str,
    weekday: int | None = None,
) -> str:
    """Calculate the initial next_run_at timestamp based on schedule settings."""
    now_trunc = truncate_to_minute(now)
    target_trunc = truncate_to_minute(target_datetime)

    if repeat_type == "一回":
        return target_trunc.isoformat()

    if repeat_type == "毎日":
        time_part = target_trunc.time()
        candidate = datetime.combine(now_trunc.date(), time_part)
        if candidate <= now_trunc:
            candidate += timedelta(days=1)
        return candidate.isoformat()

    if repeat_type == "毎週":
        if weekday is None or not (0 <= weekday <= 6):
            raise ValueError("weekday must be between 0 and 6 for 毎週")

        time_part = target_trunc.time()
        candidate = datetime.combine(now_trunc.date(), time_part)

        days_ahead = weekday - candidate.weekday()
        if days_ahead < 0 or (days_ahead == 0 and candidate <= now_trunc):
            days_ahead += 7

        candidate += timedelta(days=days_ahead)
        return candidate.isoformat()

    raise ValueError(f"Unknown repeat_type: {repeat_type}")


def calculate_next_run_after_completion(
    now: datetime, current_next_run_str: str, repeat_type: str
) -> str | None:
    """Calculate the next_run_at after a task is completed, advancing to the future."""
    if repeat_type == "一回":
        return None

    try:
        current_next = datetime.fromisoformat(current_next_run_str)
    except ValueError:
        return None

    now_trunc = truncate_to_minute(now)

    if repeat_type == "毎日":
        step = timedelta(days=1)
    elif repeat_type == "毎週":
        step = timedelta(days=7)
    else:
        return None

    next_dt = current_next + step
    while next_dt <= now_trunc:
        next_dt += step

    return next_dt.isoformat()


def backfill_migration_next_run(
    now: datetime, remind_at: str, repeat_type: str
) -> tuple[str, int | None]:
    """Calculate the next_run_at and weekday for migration backfill."""
    now_trunc = truncate_to_minute(now)
    try:
        h, m = map(int, remind_at.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
    except ValueError:
        h, m = 9, 0

    try:
        candidate = datetime.combine(now_trunc.date(), datetime.min.time()).replace(
            hour=h, minute=m
        )
    except ValueError:
        candidate = datetime.combine(now_trunc.date(), datetime.min.time()).replace(
            hour=9, minute=0
        )

    if repeat_type == "毎週":
        weekday = now_trunc.weekday()
        if candidate <= now_trunc:
            candidate += timedelta(days=7)
        return candidate.isoformat(), weekday

    # 一回・毎日
    if candidate <= now_trunc:
        candidate += timedelta(days=1)
    return candidate.isoformat(), None

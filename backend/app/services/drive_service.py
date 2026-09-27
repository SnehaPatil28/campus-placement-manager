from datetime import datetime, timezone
from typing import List
from app.models.drive import PlacementDrive, DriveStatus


def parse_csv_list(csv_str: str | None) -> List[str]:
    """Parses a comma-separated string into a list of cleaned, non-empty strings."""
    if not csv_str:
        return []
    return [item.strip() for item in csv_str.split(",") if item.strip()]


def format_list_to_csv(items: List[str] | None) -> str:
    """Formats a list of strings into a standardized comma-separated string."""
    if not items:
        return ""
    cleaned = [item.strip() for item in items if item.strip()]
    return ",".join(cleaned)


def get_evaluated_drive_status(drive: PlacementDrive) -> DriveStatus:
    """Dynamically evaluates drive status based on current UTC time vs application deadline.

    If current UTC time > application deadline, status automatically returns CLOSED.
    Otherwise, returns the stored drive status (OPEN or UPCOMING).
    """
    now_utc = datetime.now(timezone.utc)
    deadline = drive.application_deadline

    # Normalize naive datetime to UTC if necessary
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    if now_utc > deadline:
        return DriveStatus.CLOSED

    return drive.status

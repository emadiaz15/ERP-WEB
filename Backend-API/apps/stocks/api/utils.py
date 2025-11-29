from django.utils.dateparse import parse_datetime

VALID_DIRECTIONS = {"ingreso", "egreso", "all", None, ""}

def parse_iso_dt(value: str):
    """Devuelve datetime o None (ISO8601)."""
    if not value:
        return None
    return parse_datetime(value)

def normalize_direction(value: str):
    v = (value or "").strip().lower()
    return v if v in VALID_DIRECTIONS else None

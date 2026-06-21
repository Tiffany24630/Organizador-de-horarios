from enum import Enum

class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class RestrictionType(str, Enum):
    ALLOWED_HOURS = "ALLOWED_HOURS"
    FORBIDDEN_HOURS = "FORBIDDEN_HOURS"
    FORBIDDEN_DAY = "FORBIDDEN_DAYS"
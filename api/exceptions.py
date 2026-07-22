class ReminderError(Exception):
    """Base exception for reminder operations."""


class InvalidReminderDate(ReminderError):
    """Raised when a day does not exist in the selected month."""


class ReminderNotFound(ReminderError):
    """Raised when a reminder ID does not exist."""


class DatabaseUnavailable(ReminderError):
    """Raised when PostgreSQL cannot complete an operation."""

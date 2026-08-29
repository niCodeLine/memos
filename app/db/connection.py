"""PostgreSQL connection factory used by services and schema setup."""

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings


def get_connection():
    """Open a PostgreSQL connection that returns rows as dictionaries.

    Using `RealDictCursor` keeps the service layer easy to read because rows can
    be returned directly to Pydantic response models.
    """

    return psycopg2.connect(settings.postgres_dsn, cursor_factory=RealDictCursor)

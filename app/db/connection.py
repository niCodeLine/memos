import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings


def get_connection():
    return psycopg2.connect(settings.postgres_dsn, cursor_factory=RealDictCursor)

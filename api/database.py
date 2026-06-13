'''
Database connection.
'''

import os
import psycopg2
import api.log as log
from api.settings import settings

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def get_connection():
    logger.debug('Accessing DB connection.')
    try:
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
        )
    except Exception as e:
        logger.error(f'DB connection failed: {e}')
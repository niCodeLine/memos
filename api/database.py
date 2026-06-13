'''
Database connection.
'''

import os
import psycopg2
import api.log as log
from api.env_ignore import *

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def get_connection():
    logger.debug('Accessing DB connection.')
    try:
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', POSTGRES_HOST),
            database=os.getenv('POSTGRES_DB', APP_DATABASE),
            user=os.getenv('POSTGRES_USER', POSTGRES_USER),
            password=os.getenv('POSTGRES_PASSWORD', POSTGRES_PASSWORD),
            port=int(os.getenv('POSTGRES_PORT', POSTGRES_PORT)),
        )
    except Exception as e:
        logger.error(f'DB connection failed: {e}')
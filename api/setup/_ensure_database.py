'''
Ensure application database exists.
'''

import psycopg2
import os
import api.log as log
from api.env_ignore import *


logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def ensure_database():

    database_name = os.getenv('POSTGRES_DB', APP_DATABASE)
    logger.debug(f'checking database {database_name}')

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', POSTGRES_HOST),
        database=ADMIN_DATABASE,
        user=os.getenv('POSTGRES_USER', POSTGRES_USER),
        password=os.getenv('POSTGRES_PASSWORD', POSTGRES_PASSWORD),
        port=os.getenv('POSTGRES_PORT', POSTGRES_PORT),
    )
    
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # check if application database exists
        cursor.execute(
            '''
            SELECT 1
            FROM pg_database
            WHERE datname = %s
            ''',
            (database_name,)
        )
        
        exists = cursor.fetchone()

        if exists:
            logger.info(f'Database "{database_name}" already exists.')

        else:
            cursor.execute(f'CREATE DATABASE {database_name}')
            logger.info(f'Database "{database_name}" created.')

        logger.debug('Database check completed.')

    except Exception as e:
        logger.exception(f'ensure_database failed: {e}')
        raise

    finally:
        cursor.close()
        conn.close()
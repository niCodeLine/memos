'''
Ensure that the application database exists.
'''

import psycopg2
import api.log as log
from api.settings import settings

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def ensure_database():

    database_name = settings.POSTGRES_DB
    logger.debug(f'Checking database {database_name}...')

    # connect to default DB
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        database='postgres',
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        port=settings.POSTGRES_PORT,
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
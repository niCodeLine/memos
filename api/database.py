'''
Databases connections.
'''

import psycopg2
import redis
import api.log as log
from api.settings import settings

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def get_PG_connection(): # PostGres connection
    '''
    Create a PostgreSQL instance.
    '''
    logger.debug('Accessing PG connection.')
    
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


def get_RD_connection(db: int = 0): # ReDis connection
    '''
    Create a Redis instance.

    :param db: Data/base Channel to connect with (0-16). Default 0.
    :type db: int
    '''
    logger.debug('Accessing RD connection.')


    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=db,
        decode_responses=True # return text insead of binari
    )

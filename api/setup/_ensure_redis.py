'''
Ensure that the application redis server exists.
'''

import redis
import api.log as log
from api.settings import settings

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def ensure_redis():

    logger.debug(f'Checking Redis...')

    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )

    try:
        # check if Redis server is running
        
        if redis_client.ping():
            logger.info(f'Redis server running.')

    except Exception as e:
        logger.exception(f'ensure_database failed: {e}')
        raise
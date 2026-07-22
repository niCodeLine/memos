'''
REDIS DataBase interactions.

codes meanings in returns:
1: OK
0: NOT OK
'''

from types import SimpleNamespace
import api.log as log
import json
from api.database import get_RD_connection

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


def redisSet(query: str, response: SimpleNamespace, db: int = 0, ex: int = 3600) -> bool:
    '''
    Cache a query.

    :param db: DataBase Channel to connect with (0-16). Default 0.
    :type db: int
    :param ex: Expiration time in seconds. Default 3600 (1h).
    :type ex: int
    '''

    logger.debug(f'Setting query {query} on Redis.')

    try:
        get_RD_connection(db).set(
            f'query:{query}',
            json.dumps(
                response.__dict__,
                default=str
                ),
            ex=ex,
            )
        logger.info(f'Query {query} set on db: {db} (ex={ex}).')
        return True
    
    except Exception as e:
        logger.warning(f'Redis setting failed; continuing without cache: {e}')
        return False



def redisGet(query: str, db: int = 0) -> SimpleNamespace | None:
    '''
    Check for query.
    '''

    logger.debug(f'Getting query {query} on Redis.')
    
    try:
        response = get_RD_connection(db).get(
            f'query:{query}'
        )
    except Exception as e:
        logger.warning(f'Redis lookup failed; continuing without cache: {e}')
        return None

    if response:
        logger.info(f'Cache hit for query: {query} (db={db}).')
        data = json.loads(response)
        return SimpleNamespace(**data)
    
    logger.debug(f'Cache miss for query {query}.')
    return None


def redisDelete(query: str, db: int = 0) -> bool:
    """Delete a cached query without making Redis a hard dependency."""

    try:
        get_RD_connection(db).delete(f'query:{query}')
        logger.info(f'Query {query} deleted from cache db: {db}.')
        return True
    except Exception as e:
        logger.warning(f'Redis deletion failed; continuing without cache: {e}')
        return False


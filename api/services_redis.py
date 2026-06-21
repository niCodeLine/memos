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


def redisSet(query: str, response: SimpleNamespace, db: int = 0, ex: int = 3600):
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
    
    except Exception as e:
        logger.error(f'Redis setting failed: {e}')
        raise



def redisGet(query: str, db: int = 0) -> SimpleNamespace | None:
    '''
    Check for query.
    '''

    logger.debug(f'Getting query {query} on Redis.')
    
    response = get_RD_connection(db).get(
        f'query:{query}'
    )

    if response:
        logger.info(f'Cache hit for query: {query} (db={db}).')
        data = json.loads(response)
        return SimpleNamespace(**data)
    
    logger.debug(f'Cache miss for query {query}.')
    return None



'''
Setup file to run on first use.
Here databases and tables are assured to be created.
'''
import api.log as log
from ._create_tables import create_tables
from ._ensure_database import ensure_database
from ._ensure_redis import ensure_redis

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)

def main():

    logger.info('Executing initialization setup.')

    ensure_database()
    create_tables()
    ensure_redis()

    logger.info('Setup completed successfully.')


if __name__ == '__main__':
    main()
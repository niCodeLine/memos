'''Tables to be created. For better scalability in a future.'''

# TODO:
# Replace user_id's definition to:
# INTEGER REFERENCES users(id)
# when table "users" is implemented.

from api.database import get_PG_connection
import api.log as log
from api.constants import MAIN_REMINDERS_TABLE

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)


TABLES = {
    MAIN_REMINDERS_TABLE:
        '''
        id SERIAL PRIMARY KEY,

        user_id INTEGER DEFAULT 1,

        day INTEGER NOT NULL CHECK(day BETWEEN 1 AND 31),
        month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),

        text TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT NOW()
        ''',
}

def create_tables():

    conn = get_PG_connection()
    cursor = conn.cursor() #type: ignore

    try:
        for tableName, tableDefinition in TABLES.items():
            cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS {tableName} (
                {tableDefinition}
                )
                '''
            )
            
            logger.info(f'Table "{tableName}" ready.')

        conn.commit() #type: ignore
        logger.info(f'Tables committed to database.')
    
    except Exception as e:
        logger.exception(f'Create table failed: {e}')
        raise

    finally:
        cursor.close()
        conn.close() #type: ignore


if __name__ == '__main__':
    create_tables()
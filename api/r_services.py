'''
API <-> DataBase interactions.

codes meanings in returns:
1: OK
0: NOT OK
'''

from types import SimpleNamespace
import api.log as log
from api.database import get_connection
from api.constants import MAIN_REMINDERS_TABLE

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)

# months properties
MONTH_DAYS = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31}

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"}


def create(*, day: int, month: int, text: str):
    '''
    Create a reminder into the database.

    Expected body:
    - day: int
    - month: int
    - text: str
    '''

    # connecting with database
    conn = get_connection()
    cursor = conn.cursor()

    # checking for valid date
    if day > MONTH_DAYS[month]:
        return SimpleNamespace(
            code = 0,
            message = f'{MONTH_NAMES[month]} does not have {day} days.',
            reminder_id = None,
        )
    
    try:
        cursor.execute(
            f'''
            INSERT INTO {MAIN_REMINDERS_TABLE}
            (day, month, text)
            VALUES (%s, %s, %s)
            RETURNING id
            ''',
            (day, month, text)
        )
        
        reminder_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.debug('Committed succesfully.')

        return SimpleNamespace(
            code = 1, 
            message = f'Reminder "{text}" saved on {day} - {MONTH_NAMES[month]}.',
            reminder_id = reminder_id,
        )
    
    except Exception as e:
        conn.rollback()
        logger.error(f'Reminder creation failed: {e}')

        return SimpleNamespace(
            code = 0,
            message = f'Could\'nt create reminder:\n{str(e)}',
            reminder_id = None,
            )

    finally:
        # closing connection
        cursor.close()
        conn.close()


def get_by_id(reminder_id: int):
    '''
    Get a reminder from the database by its ID.
    '''

    # connecting with database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f'''
            SELECT day, month, text, created_at FROM {MAIN_REMINDERS_TABLE}
            WHERE id = %s
            ''',
            (reminder_id,)
            )
        
        row = cursor.fetchone()
        
        if not row:
            return SimpleNamespace(
            code = 0,
            message = f'Reminder with id {reminder_id} not found.',
            reminder= None,
            )
        
        day = row[0]
        month = row[1]
        text = row[2]
        created_at = row[3]
        
        return SimpleNamespace(
            code = 1, 
            message = f'Reminder "{text}" on {day} - {MONTH_NAMES[month]} created at {created_at}, found with id {reminder_id}.',
            reminder = {
                'reminder_id': reminder_id,
                'day': day,
                'month': month,
                'month_name': MONTH_NAMES[month],
                'text': text,
                'created_at': created_at},
            )
    
    except Exception as e:
        conn.rollback()
        logger.error(f'Getting reminder failed: {e}')

        return SimpleNamespace(
            code = 0,
            message = f'Could\'nt get reminder by id {reminder_id}:\n{str(e)}',
            reminder = None,
            )

    finally:
        # closing connection
        cursor.close()
        conn.close()


def get(day: int | None = None, month: int | None = None, text: str | None = None,):
    '''
    Get one or multiple reminders from database. 
    Can use optional filters.
    '''

    # connecting with database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = f'''
            SELECT id, day, month, text, created_at FROM {MAIN_REMINDERS_TABLE}
            WHERE 1=1
            ''' # WHERE 1=1 added so next posible params can be added with AND
        
        # adding parameters
        params = []

        if day is not None:
            query += ' AND day = %s'
            params.append(day)
            logger.debug(f'day "{day}" added.')

        if month is not None:
            query += ' AND month = %s'
            params.append(month)
            logger.debug(f'month "{month}" added.')

        if text is not None:
            query += ' AND text ILIKE %s'
            params.append(f'%{text}%')
            logger.debug(f'text "{text}" added.')


        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        if not rows:
            return SimpleNamespace(
            code = 0,
            message = f'None reminders found.',
            reminders= None,
            )

        reminders_data = [
            {
                'reminder_id': row[0],
                'day': row[1],
                'month': row[2],
                'month_name': MONTH_NAMES[row[2]],
                'text': row[3],
                'created_at': row[4]}
            for row in rows
            ]

        return SimpleNamespace(
            code = 1, 
            message = f'{len(reminders_data)} reminder(s) found.',
            reminders = reminders_data,
            )
    
    except Exception as e:
        conn.rollback()
        logger.error(f'Getting reminders failed: {e}')

        return SimpleNamespace(
            code = 0,
            message = f'Could\'nt get reminders:\n{str(e)}',
            reminders = None,
            )

    finally:
        # closing connection
        cursor.close()
        conn.close()


def delete(reminder_id: int):
    '''
    Delete a reminder from database.
    '''

    # connecting with database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            DELETE FROM reminders
            WHERE id = %s
            RETURNING day, month, text, created_at
            ''',
            (reminder_id,)
            )

        row = cursor.fetchone()
        conn.commit()
        
        if not row:
            return SimpleNamespace(
            code = 0,
            message = f'Reminder with id {reminder_id} not found.',
            reminder= None,
            )

        day = row[0]
        month = row[1]
        text = row[2]
        created_at = row[3]
        
        return SimpleNamespace(
            code = 1, 
            message = f'Reminder {reminder_id} "{text}" on {day} - {MONTH_NAMES[month]} created at {created_at}, deleted.',
            reminder = {
                'reminder_id': reminder_id,
                'day': day,
                'month': month,
                'month_name': MONTH_NAMES[month],
                'text': text,
                'created_at': created_at},
            )

    except Exception as e:
        conn.rollback()
        logger.error(f'Deleting reminder failed: {e}')

        return SimpleNamespace(
            code = 0,
            message = f'Could\'nt delete reminder with id {reminder_id}:\n{str(e)}',
            reminder = None,
            )

    finally:
        # closing connection
        cursor.close()
        conn.close()
    
    
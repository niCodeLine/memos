'''
Sending the requests to the database\'s service.

This 'routes' folder is created for scalability, in case of bigger inspiration.
The functions are repeated to make them usable with assistants (adk) implementations.
'''

# NOTE
# "schemas" is used when data comes from the body of the requests (POST).
# While "Query" is used when data is coming from in the URL (GET).

from fastapi import APIRouter, Query
from api.schemas import *
import api.log as log
import api.services_db as services_db

logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)

# settings
router = APIRouter(
    prefix = "/reminders",
    tags = ["reminders"]
)
logger.debug('API router set from routes.reminders')


# functions
async def create_reminder(text: str, day: int, month: int):
    '''
    Create a reminder with a specific text, day, and month.

    Args:
        text (str): The content of the reminder.
        day (int): The day of the month (1-31).
        month (int): The month number (1-12).
    '''
    logger.debug(f'Creating reminder: {locals()}')
    
    response = services_db.create(
        day=day,
        month=month,
        text=text,
    )

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder": response.reminder,
    }


async def get_reminder_by_id(reminder_id: int):
    '''
    Get a reminder by ID number.

    Args:
        reminder_id (int): ID of the reminder to get.
    '''
    logger.debug(f'Searching reminder_id: {reminder_id}')

    response = services_db.get_by_id(reminder_id)

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder": response.reminder,
    }


async def get_reminders(
    day: int | None = None,
    month: int | None = None,
    text: str | None = None,
    ):
    '''
    Get reminders. Can use optional filters.

    Args:
        day (int | None): Optional day of the month (1-31) to filter reminders.
        month (int | None): Optional month number (1-12) to filter reminders.
        text (str | None): Optional text or keyword to search within the reminders.
    '''
    logger.debug(f'Searching reminders: {locals()}')
    
    response = services_db.get(
        day=day,
        month=month,
        text=text,
    )

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminders": response.reminders,
    }


async def delete_reminder(reminder_id: int):
    '''
    Delete a reminder by ID number.

    Args:
        reminder_id (int): ID of the reminder to delete.
    '''
    logger.debug(f'Deleting reminder_id: {reminder_id}')

    response = services_db.delete(reminder_id)

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder": response.reminder,
    }



# FastAPI functions

@router.post("/")
async def create_reminder_endpoint(reminder: CreateReminder):
    '''
    Create a reminder.

    Expected body:
    - text: str
    - day: int
    - month: int
    '''
    
    return await create_reminder(
        text=reminder.text,
        day=reminder.day,
        month=reminder.month
    )


@router.get("/{reminder_id}")
async def get_reminder_by_id_endpoint(reminder_id: int):
    '''
    Get reminder by ID number.
    '''
    
    return await get_reminder_by_id(reminder_id)


@router.get("/")
async def get_reminders_endpoint(
    day: int | None = Query(None, ge=1, le=31),
    month: int | None = Query(None, ge=1, le=12),
    text: str | None = Query(None, min_length=1, max_length=100),
    ):
    '''
    Get reminders. Can use optional filters.
    '''
    
    return await get_reminders(
        day=day,
        month=month,
        text=text
    )


@router.delete("/{reminder_id}")
async def delete_reminder_endpoint(reminder_id: int):
    '''
    Delete a reminder. 
    This is done via reminde_id gotten when created or searched.
    '''
    
    return await delete_reminder(reminder_id)
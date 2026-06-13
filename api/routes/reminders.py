'''
This 'routes' folder is created for scalability, in case of bigger inspiration.

Sending the requests to the database\'s service.
'''

from fastapi import APIRouter, Query
from api.schemas import *
import api.log as log
import api.r_services as r_services

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

@router.post("/")
async def create_reminder(reminder: CreateReminder):
    '''
    Create a reminder.

    Expected body:
    - text: str
    - day: int
    - month: int
    '''
    logger.debug(f'Creating reminder: {locals()}')
    
    response = r_services.create(
        day = reminder.day,
        month = reminder.month,
        text = reminder.text,
    )

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder_id": response.reminder_id,
    }

@router.get("/{reminder_id}")
async def get_reminder_by_id(reminder_id: int):
    '''
    Get reminder by ID.
    '''
    logger.debug(f'Searching reminder_id: {reminder_id}')

    response = r_services.get_by_id(reminder_id)

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder": response.reminder,
    }

@router.get("/")
async def get_reminders(
    day: int | None = Query(None, ge=1, le=31),
    month: int | None = Query(None, ge=1, le=12),
    text: str | None = Query(None, min_length=1, max_length=100),
    ):
    '''
    Get reminders. Can use optional filters.
    '''
    logger.debug(f'Searching reminders: {locals()}')
    
    response = r_services.get(
        day = day,
        month = month,
        text = text,
    )

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminders": response.reminders,
    }

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int):
    '''
    Delete a reminder. 
    This is done via reminde_id gotten when created or searched.
    '''
    logger.debug(f'Deleting reminder_id: {reminder_id}')

    response = r_services.delete(reminder_id)

    logger.info(response.message)

    return {
        "code": response.code,
        "message": response.message,
        "reminder_id": response.reminder_id,
    }
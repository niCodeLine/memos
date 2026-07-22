'''
Schemas for defining requests entry format.
'''

from pydantic import BaseModel, Field

class ReminderFields(BaseModel):
    text: str = Field(
        min_length=1, 
        max_length=100,
        )
    
    day: int = Field(
        ge=1,
        le=31,
        )
    
    month: int = Field(
        ge=1,
        le=12,
        )


class CreateReminder(ReminderFields):
    pass


class UpdateReminder(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=100)
    day: int | None = Field(default=None, ge=1, le=31)
    month: int | None = Field(default=None, ge=1, le=12)

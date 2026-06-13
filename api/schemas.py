'''
Schemas for defining requests entry format.
'''

from pydantic import BaseModel, Field

class CreateReminder(BaseModel):
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

import datetime
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class MessageRead(BaseModel):
    id: int
    text: str
    category: str
    date: datetime
    user_id: int
    
    class Config: 
        from_attributes = True

class MessageWithUserFlat(BaseModel):
   
    id: int
    user_id: int
    text: str
    chat_id: int
    message_id: int
    date: datetime

   
    category: Optional[str] = None
    is_request: Optional[bool] = None

 
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


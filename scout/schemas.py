import datetime
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional,Union

class MessageRead(BaseModel):
    id: int
    text: str
    category: str
    date: datetime
    user_id: Union[int,None]
    
    class Config: 
        from_attributes = True

class MessageWithUserFlat(BaseModel):
   
    id: int
    user_id: Union[int,None]
    text: str
    chat_id: int
    chat_signed_id: int
    message_id: int
    date: datetime
    peer_type: str

   
    category: Optional[str] = None
    is_request: Optional[bool] = None

 
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    class Config: 
        from_attributes = True

class TelegramChatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tg_chat_id: int
    title: str
    peer_type: str
    description: Optional[str] = None 
    username: Optional[str] = None
    access_hash: Union[int,None]
    is_megagroup: Union[bool,None]
    is_broadcast: Union[bool,None]
    is_forum: Union[bool,None]
    is_verified: Union[bool,None]
    is_scam: Union[bool, None]
    is_fake: Union[bool, None]
    is_restricted: Union[bool,None]
    participants_count: Union[int,None]
    admins_count: Union[int, None]
    kicked_count: Union[int,None]
    banned_count: Union[int,None]
    

class TelegramUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    username: Union[str,None]
    first_name: Union[str,None]
    last_name: Union[str,None]
    phone: Union[str,None]

class UserCreate(BaseModel):
    username: str
    password: str



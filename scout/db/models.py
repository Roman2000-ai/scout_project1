from re import S
from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, Boolean,
    DateTime, UniqueConstraint, Index, CheckConstraint, exc, func,
    ForeignKey,JSON 
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
try:
    from scout.utils import utcnow
except:
    from utils import utcnow
Base = declarative_base()



class MessageTelegram(Base):

    __tablename__ = "messagestelegram"

    id = Column(Integer,primary_key=True)
    user_id = Column(BigInteger,nullable=True)
    category = Column(String(70),nullable=True,index=True)
    is_request = Column(Boolean)
    text = Column(String(500))
    chat_signed_id = Column(BigInteger,nullable=True)
    chat_id = Column(ForeignKey("telegramchat.id",ondelete="CASCADE"),nullable=False)
    message_id = Column(BigInteger,nullable=False)
    date = Column(DateTime,nullable=False)
    peer_type = Column(String(10), nullable= False)


    chat = relationship(
        "TelegramChat",
        back_populates="messages",
        lazy="joined"                  
    )
    __table_args__ = (
    UniqueConstraint("chat_id", "message_id", name="ux_msg_in_chat"),
)


    
class UserTelegram(Base):
    __tablename__ = "usertelegram"

    id = Column(Integer, primary_key=True)
    user_id=  Column(BigInteger,index=True,nullable=False)    
    username = Column(String(32), index=True, nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name  = Column(String(64), nullable=True)
    is_bot = Column(Boolean, default=False)
    phone = Column(String(32), nullable=True)      
    language_code = Column(String(8), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
   



class TelegramChat(Base):
    __tablename__ = "telegramchat"
    
    id = Column(Integer,primary_key=True)
    tg_chat_id = Column(BigInteger,nullable=False)
    title= Column(String(255),index=True)
    peer_type =  Column(String(20),nullable=False)
    description = Column(Text, nullable=True)
    username = Column(String,nullable=True,index=True)
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    access_hash = Column(BigInteger, nullable=True)                
    is_megagroup = Column(Boolean, nullable=True)                   
    is_broadcast = Column(Boolean, nullable=True)                   
    is_forum = Column(Boolean, nullable=True)                      

    is_verified = Column(Boolean, nullable=True)                    
    is_scam = Column(Boolean, nullable=True)                        
    is_fake = Column(Boolean, nullable=True)                        
    is_restricted = Column(Boolean, nullable=True)                 

    
    participants_count = Column(Integer, nullable=True)             
    admins_count = Column(Integer, nullable=True)                  
    kicked_count = Column(Integer, nullable=True)                   
    banned_count = Column(Integer, nullable=True)                  
    online_count = Column(Integer, nullable=True)                   

    slowmode_seconds = Column(Integer, nullable=True)               
    pinned_msg_id = Column(BigInteger, nullable=True)               
    linked_chat_id = Column(BigInteger, nullable=True)              

    available_reactions = Column(JSON, nullable=True)               
    stickerset_id = Column(BigInteger, nullable=True)               
    invite_link = Column(String, nullable=True) 
    
    messages = relationship(
        "MessageTelegram",                 
        back_populates="chat",     
        cascade="all, delete-orphan",
        passive_deletes=True,     
        lazy="selectin"            
    )


    __table_args__ = (
        UniqueConstraint("peer_type", "tg_chat_id", name="ux_tg_peer"),  
        Index("ix_tg_username", "username"),                            
        CheckConstraint("peer_type IN ('user','chat','channel')", name="ck_peer_type"),  
    )

class User(Base):
    __tablename__ = "user"
    id = Column(Integer,nullable=False,primary_key=True)
    username = Column(String, nullable=False, index=True)
    hashed_password = Column(String,nullable=False)

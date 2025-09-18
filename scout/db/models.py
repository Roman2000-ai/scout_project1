from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime,ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()



class MessageTelegram(Base):

    __tablename__ = "messagestelegram"

    id = Column(Integer,primary_key=True)
    user_id = Column(BigInteger,nullable=False)
    category = Column(String(70),nullable=True,index=True)
    is_request = Column(Boolean)
    text = Column(String(500))
    chat_id = Column(BigInteger,nullable=False)
    message_id = Column(BigInteger,nullable=False,unique=True)
    date = Column(DateTime,nullable=False)


    
class UserTelegram(Base):
    __tablename__ = "usertelegram"

    id = Column(BigInteger, primary_key=True)      
    username = Column(String(32), index=True, nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name  = Column(String(64), nullable=True)
    is_bot = Column(Boolean, default=False)
    phone = Column(String(32), nullable=True)      
    language_code = Column(String(8), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
   
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from .models import MessageTelegram, UserTelegram, TelegramChat,User
from sqlalchemy import select, insert, func, or_
from typing import Union,Dict,Any
from schemas import MessageWithUserFlat,TelegramChatSchema, TelegramUserSchema
from typing import List
from passlib.context import CryptContext
from security import  get_password_hash, verify_password


#engine = create_async_engine("sqlite+aiosqlite:///scout.db")
#async_session_factory = async_sessionmaker(engine, expire_on_commit=False)




async  def  get_telegram_chat_by_id_and_type(session,chat_id,peer_type):
    """получаю чат с помощью peer_type  и id"""

    query = select(TelegramChat).where(
            TelegramChat.peer_type == peer_type,
            TelegramChat.tg_chat_id == chat_id

        ).limit(1)

    res =  await session.execute(query)
    chat = res.scalar()

    return chat

async  def create_telegram_message(session:AsyncSession,message: dict):
    """создает  MessageTelegram в DB"""
    #async with async_session_factory() as session:
    chat = await get_telegram_chat_by_id_and_type(session,message.get("chat_signed_id"),message.get("peer_type"))
    if chat:
        chat_id = chat.id
    else:
        chat_id = None
    new_message =  MessageTelegram(
        user_id=message.get("user_id"),
        category=message.get("category"),
        is_request=bool(message.get("is_service_request", False)),
        text=message.get("text") or "",
        chat_signed_id=message.get("chat_signed_id"),
        chat_id=chat_id,
        message_id=message.get("message_id"),
        date=message.get("date"),
        peer_type = message.get("peer_type"),
    )
    session.add(new_message)

    await session.commit()

    print(f"новое сообщение было добавлено в db. message_id:{new_message.message_id}, ID(db){new_message.id}")


async def get_telegram_message(session:AsyncSession,id_db_message: int) -> Union[MessageTelegram,None]:
    """возвращает TelegramMessage  по id"""
    #async with async_session_factory() as session:

    query = select(MessageTelegram).where(MessageTelegram.id == id_db_message,MessageTelegram.is_request== True)


    result = await session.execute(query)

    message = result.scalar_one_or_none()

    return message



async def get_telegram_messages_by_category(session:AsyncSession,category:str,skip:int = 0,limit:int = 100) -> Union[list[MessageTelegram],None]:
    """ищет TelegramMessages  по категории и возвращает  list[TelegramMessage]"""
    #async with async_session_factory() as session:

    query = select(MessageTelegram).where(MessageTelegram.category == category).offset(skip).limit(limit)

    result = await session.execute(query)

    messages = result.scalars().all()

    return messages


async def update_telegram_message(session:AsyncSession,message: dict) -> bool:
    """Находит  TelegramMessage по id и обновляет его данные"""
    #async with  async_session_factory() as session:


    query = select(MessageTelegram).where(MessageTelegram.id == message['id'])

    result  = await session.execute(query)

    message_db = result.scalar_one_or_none()

    if not message_db:
        print("telegrammessage не найдено в бз")
        return False
    for key in message:
        if key == 'id':
            continue
    
        #message_db.key = message[key]
        setattr(message_db,key,message[key])

    session.add(message_db)

    await session.commit()
    print(f"Данные обновлены у  MessageTelegram id: {message_db.id}")
    return True


        

async def delete_telegram_message_by_id(session:AsyncSession,id_db_message: int) -> bool:
    """Поиск MessageTelegram по id и удаление"""
    #async with async_session_factory() as session:
    
    query = select(MessageTelegram).where(MessageTelegram.id == id_db_message)

    result = await session.execute(query)

    message = result.scalar_one_or_none()

    if not message:
        print("MessageTelegram не найден")
        return False
    session.delete(message)
    await session.commit()

    return True


async def create_or_update_user_telegram(
    session: AsyncSession,
    user: Dict[str, Any],
    commit: bool = True,
) -> UserTelegram:
    """
    Создаёт или обновляет UserTelegram по user['id'].
    Ожидаемые ключи: user_id, username, first_name, last_name, is_bot, phone, language_code.
    """
    if "user_id" not in user:
        raise ValueError("user must contain 'id'")

    query = select(UserTelegram).where(UserTelegram.user_id == user["user_id"])
    result = await session.execute(query)
    user_db = result.scalar_one_or_none()

    if not user_db:
        user_db = UserTelegram(
            user_id=user["user_id"],
            username=user.get("username"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            is_bot=bool(user.get("is_bot", False)),
            phone=user.get("phone"),
            language_code=user.get("language_code"),
        )
        session.add(user_db)
        if commit:
            await session.commit()
        print(f"Создан UserTelegram id={user_db.id}, username={user_db.username}")
        return user_db

    for field in ("username", "first_name", "last_name", "is_bot", "phone", "language_code"):
        if field in user:
            setattr(user_db, field, user[field])

    if commit:
        await session.commit()
    print(f"Обновлён UserTelegram id={user_db.id}, username={user_db.username}")
    return user_db






async def get_messages_with_user_by_category_flat(
    session: AsyncSession,
    category: str,
    skip: int = 0,
    limit: int = 100,
) -> List[MessageWithUserFlat]:
    q = (
        select(
            MessageTelegram.id.label("id"),
            MessageTelegram.user_id.label("user_id"),
            MessageTelegram.text.label("text"),
            MessageTelegram.chat_id.label("chat_id"),
            MessageTelegram.message_id.label("message_id"),
            MessageTelegram.date.label("date"),
            MessageTelegram.category.label("category"),
            MessageTelegram.is_request.label("is_request"),
            MessageTelegram.peer_type.label("peer_type"),
            MessageTelegram.chat_signed_id.label("chat_signed_id"),
            
            UserTelegram.username.label("username"),
            UserTelegram.first_name.label("first_name"),
            UserTelegram.last_name.label("last_name"),
            UserTelegram.phone.label("phone"),
        )
        .join(UserTelegram, UserTelegram.id == MessageTelegram.user_id, isouter=True)  
        .where(MessageTelegram.category == category)
        .order_by(MessageTelegram.date.desc())
        .offset(skip)
        .limit(limit)
    )

    res = await session.execute(q)
    rows = res.mappings().all() 


    return [MessageWithUserFlat(**row) for row in rows]



async def create_or_update_telegramchat(session,chat_data:dict):
    
    """добавляет телеграм чат  в  базу даннызх"""
    async with  session() as session:
        chat = await session.scalar(
        select(TelegramChat).where(
            TelegramChat.peer_type == chat_data["peer_type"],
            TelegramChat.tg_chat_id == chat_data["tg_chat_id"],
        )
    )
        if chat:
            print("чат уже сущестует")
            await session.commit()
            return chat, False
        chat = TelegramChat(**chat_data)

        session.add(chat)

        await session.commit()
        print("чат был добвален в db")
        return chat,True



async def get_chats_from_db(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 100,
    q: str = None
)-> List[TelegramChatSchema]:
    if q:
        pat = f"%{q.lower()}%"  
        
        query = select(TelegramChat).offset(offset).limit(limit).where(
    func.lower(TelegramChat.title).like(pat) |   
    func.lower(TelegramChat.description).like(pat)
)
    else:
        query = select(TelegramChat).offset(offset).limit(limit)
    
    res = await session.execute(query)

    chats = res.scalars().all()
    return [TelegramChatSchema.from_orm(chat) for chat in chats]
    
    
async def  get_messages_by_id_chat_db(
    session: AsyncSession,
    chat_id: int,
    offset: int = 0,
    limit: int = 100,
)-> List[MessageWithUserFlat]:
    query = (
        select(
            MessageTelegram.id.label("id"),
            MessageTelegram.user_id.label("user_id"),
            MessageTelegram.text.label("text"),
            MessageTelegram.chat_id.label("chat_id"),
            MessageTelegram.message_id.label("message_id"),
            MessageTelegram.date.label("date"),
            MessageTelegram.category.label("category"),
            MessageTelegram.is_request.label("is_request"),
            MessageTelegram.peer_type.label("peer_type"),
            MessageTelegram.chat_signed_id.label("chat_signed_id"),
            
            UserTelegram.username.label("username"),
            UserTelegram.first_name.label("first_name"),
            UserTelegram.last_name.label("last_name"),
            UserTelegram.phone.label("phone"),
        )
        .join(UserTelegram, UserTelegram.id == MessageTelegram.user_id, isouter=True)  
        .where(MessageTelegram.chat_id == chat_id)
        .order_by(MessageTelegram.date.desc())
        .offset(offset)
        .limit(limit)
    )
    res =  await session.execute(query)
    messages = res.mappings().all()
    return [MessageWithUserFlat(**message) for message in messages]
    


async def get_users_db(session: AsyncSession,offset:int=0,limit:int=100):
    qeury = select(UserTelegram).offset(offset).limit(limit)

    res = await session.execute(qeury)

    users = res.scalars().all()

    return [TelegramUserSchema.from_orm(user) for user in users]


async def get_user_by_user_id_db(session:AsyncSession,user_id:int):
    query = select(UserTelegram).where(UserTelegram.user_id == user_id)
    res = await session.execute(query)
    users = res.scalars().all()
    return [TelegramUserSchema.from_orm(user) for user in users]

async def login_for_access_token(session,form_data):

    query = select(User).where(User.username == form_data.username)

    res = await session.execute(query)

    user = res.scalar_one_or_none()

    if  not user:
        return False, None

    if verify_password(form_data.password, user.hashed_password):
        return True , user
    



async def get_user_by_username(session,user_data):
    
    query = select(User).where(User.username == user_data.username)
    res = await  session.execute(query)

    user = res.scalar_one_or_none()
    if user:
          return user
    else:
        return None



async def create_user(session,user_data):
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username,hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

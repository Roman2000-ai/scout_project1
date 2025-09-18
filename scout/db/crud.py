import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from .models import MessageTelegram, UserTelegram
from sqlalchemy import select
from typing import Union,Dict,Any
from schemas import MessageWithUserFlat
from typing import List



#engine = create_async_engine("sqlite+aiosqlite:///scout.db")
#async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async  def create_telegram_message(session:AsyncSession,message: dict):
    """создает  MessageTelegram в DB"""
    #async with async_session_factory() as session:
    new_message =  MessageTelegram(
        user_id=message.get("user_id"),
        category=message.get("category"),
        is_request=bool(message.get("is_service_request", False)),
        text=message.get("text") or "",
        chat_id=message.get("chat_id"),
        message_id=message.get("message_id"),
        date=message.get("date")
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
    Ожидаемые ключи: id, username, first_name, last_name, is_bot, phone, language_code.
    """
    if "id" not in user:
        raise ValueError("user must contain 'id'")

    query = select(UserTelegram).where(UserTelegram.id == user["id"])
    result = await session.execute(query)
    user_db = result.scalar_one_or_none()

    if not user_db:
        user_db = UserTelegram(
            id=user["id"],
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


from telethon.sync import TelegramClient, events
import os 
from dotenv import load_dotenv
import re
import asyncio
from utils import parse_message_from_telegram,parse_message_from_message,prepare_data_to_create_telegram_chat
import threading
from queue import Queue
from message_queue import worker
from db.crud import create_or_update_telegramchat
from db.database import get_session
from scout.db.database import get_session
from telethon.utils import get_peer_id

from telethon.tl import functions, types 
try:
    from telethon.tl.functions.channels import GetFullChannel
except ImportError:
    from telethon.tl.functions.channels import GetFullChannelRequest as GetFullChannel

try:
    from telethon.tl.functions.messages import GetFullChat
except ImportError:
    from telethon.tl.functions.messages import GetFullChatRequest 






load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TELEGRAM_CHATS = os.getenv("TELEGRAM_CHATS").split(",")
print(TELEGRAM_CHATS)

PATTERNS = [
    r"\bищ\w+\b",                            
    r"\bразыск\w+\b",                         
    r"\bподыск\w+\b",                          
    r"\bнужн\w+\b",
    r"\bнужен\b",                            
    r"\bпонадоб\w+\b",                         
    r"\bтребуетс\w*\b|\bпотребуетс\w*\b",      
    r"\bнеобход\w+\b",                         
    r"\bподскажите\b|\bпосоветуйте\b|\bпорекомендуйте\b",
    r"\bзакаж\w+\b|\bзаказать\b",             
    r"\bоплачу\b|\bзаплачу\b|\bготов\w*\s+оплатить\b|\bготов\w*\s+заплатить\b",
    r"\bвыполнит\w*\b|\bсдела\w*\b|\bсможет\w*\s+сделать\b|\bкто\s+может\s+сделать\b",
    r"\bнужн\w*\s+(сделать|починить|установить|настроить|перевезти|доставить|собрать|оформить|убрать|отремонтировать)\b",
    r"\bсрочн\w*\s+нужн\w*\b|\bнужно\s+сегодня\b|\bнужно\s+(прямо\s+)?сейчас\b",
    r"\bищу\s+(мастер|исполнител|подрядчик|фрилансер)\w*\b",
    r"\bнужен\s+(мастер|исполнитель|подрядчик|курьер|сантехник|электрик)\w*\b",
]

async def get_information_from_chat_and_create_in_db(chats_entity,client):
    for chat_entity in chats_entity:
        add_info = {}
        print(F"говоятся данные чата {chat_entity.title} для добвления в db")
        if isinstance(chat_entity,types.Chat):
            add_info["peer_type"] = "chat"
            print(f"{chat_entity.title} это  маленькая группа")
            full = await  client(functions.messages.GetFullChatRequest(chat_id=chat_entity.id))
            add_info["description"] = getattr(full.full_chat,"about",None)
        elif isinstance(chat_entity, types.Channel):
            print(f"{chat_entity.title} это большая группа")
            add_info["peer_type"] = "channel"

            full = await client(functions.channels.GetFullChannelRequest(channel=chat_entity))
            add_info["description"] = getattr(full.full_chat,"about",None)
            # возможно нало будет получить больше информации,жду ответа
        parse_data = prepare_data_to_create_telegram_chat(chat_entity,add_info,full)
        print(parse_data) 
        await create_or_update_telegramchat(get_session,parse_data)







async def create_client_telegram(q: asyncio.Queue):
    compiled_patterns = [re.compile(p, flags=re.IGNORECASE | re.UNICODE) for p in PATTERNS]
    async with TelegramClient("my_session",API_ID,API_HASH) as client:
        
        me = await client.get_me()
        name_chats = TELEGRAM_CHATS

        print(f"username: {me.username}")

        target_chats = []
        #target_chats = [chat for chat in client.iter_dialogs if chat.name.lower() == name_chat ]
        async for chat in client.iter_dialogs():
            if chat.name.lower() in  name_chats:
                 print("чат найден!!!")
                 target_chats.append(chat.entity)
        await get_information_from_chat_and_create_in_db(target_chats,client)
            
        # for chat in target_chats:
        #     async for msg in client.iter_messages(chat, limit=100):
        #         text = msg.text.lower() if msg.text else ""
        #         if any(pat.search(text) for pat in compiled_patterns):
        #             print("сообщение проходит фильтр")
        #             message = parse_message_from_message(msg)
        #             sender = await msg.get_sender()
        #             if sender:
        #                 message["username"] = getattr(sender, "username", None)
        #                 message["first_name"] = getattr(sender, "first_name", None)
        #                 message["last_name"] = getattr(sender, "last_name", None)
        #                 message["is_bot"] = bool(getattr(sender, "bot", False))
        #                 message["phone"] = getattr(sender, "phone", None)
        #                 message["language_code"] = getattr(sender, "lang_code", None)

        #             await q.put(message)
        #             print(q)
        #             print("сообщение добавлено в очередь")

            



        @client.on(events.NewMessage(chats=target_chats))
        async def new_message_handler(event):
            print("поймано новое сообщение")
            text = event.text.lower()
            if any(pat.search(text) for pat in compiled_patterns):
                print("сообщение проходит фильтр")
                message = parse_message_from_telegram(event)

                sender = await event.get_sender()
                if sender:
                    message["username"] = getattr(sender, "username", None)
                    message["first_name"] = getattr(sender, "first_name", None)
                    message["last_name"] = getattr(sender, "last_name", None)
                    message["is_bot"] = bool(getattr(sender, "bot", False))
                    message["phone"] = getattr(sender, "phone", None)
                    message["language_code"] = getattr(sender, "lang_code", None)

                await q.put(message)
                print(q)
                print("сообщение добавлено в очередь")

        await client.run_until_disconnected()



async def main():
    q = asyncio.Queue()

    worker_task = asyncio.create_task(worker(q))


    await create_client_telegram(q)

if __name__ == "__main__":
    

    asyncio.run(main())


    



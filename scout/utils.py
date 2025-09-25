from email import message_from_binary_file
from email.message import EmailMessage
from typing import Union, Dict
from datetime import datetime, timezone
from telethon.utils import get_peer_id
from telethon.tl import types


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_message_from_telegram(event) -> dict:
    """ 
    собирает данные о сообщения из  объекта Event

    """

    result = {}
    message = event.message

    result["user_id"] = message.sender_id
    result["chat_signed_id"] = int(message.chat_id)
    result["chat_id"] = None
    result["message_id"] = message.id
    result["date"] = message.date
    result["text"] = message.text
    result["category"] = None
    result["is_service_request"] = None
    print(f"Это message_peertype - {message.peer_id}")
    if isinstance(message.peer_id, types.PeerUser):
        pass
    elif isinstance(message.peer_id, types.PeerChat):
        print("это чат")
        result["peer_type"] = "chat"
    elif isinstance(message.peer_id, types.PeerChannel):
        print("это канал")
        result["peer_type"] = "channel"
    return result

def prepare_for_api_ai_request(messages: list[dict]) -> list[dict]:
    """
    подготавливает ланные для запроса в ai api,убирает чувствиетльные данные

    """

    msgs = []

    for message in messages:
        msg = {
            "message_id": message["message_id"],  
            "text": message["text"],
            "category": None,
            "is_service_request": None,
        }
 

        msgs.append(msg)
    
    return msgs


def add_message_data(messages: list[dict],respond_messages:list[dict]) -> Union[list[dict],None]:
    """
        добавляет данные из ответа от ai api в сообщения
    """
    print("запустилась функция  add_message_data")
    print(" Ключи ответа:", respond_messages[0].keys())
    print("ключи сообщений:", messages[0].keys())
    print(f"{len(messages)},{len(respond_messages)}")
    try:
        for ind in range(len(messages)):
            if messages[ind]["message_id"] == respond_messages[ind]["message_id"]:
                messages[ind]["category"] = respond_messages[ind]["category"]
                messages[ind]["is_service_request"] = respond_messages[ind]["is_service_request"]
            else:
                print("id не совпадют при добавлений данных")
                return None
        return messages
    except Exception as e:
        print(" Ошибка в add_message_data:", e)
        return None

def parse_message_from_message(msg) -> Dict:
    text_src = getattr(msg, "raw_text", None) or getattr(msg, "text", "") or ""
    return {
        "user_id": getattr(msg, "sender_id", None),
        "chat_id": getattr(msg, "chat_id", None),
        "message_id": getattr(msg, "id", None),
        "date": getattr(msg, "date", None),
        "text": text_src,
        "category": None,
        "is_service_request": False,
    }
    

def prepare_data_to_create_telegram_user(message: dict) -> dict:

    user = {}

    user["username"] = message["username"]
    user["first_name"] = message["first_name"]
    user["last_name"] = message["last_name"]
    user["is_bot"] = message["is_bot"]
    user["phone"] = message["phone"]
    user["language_code"] = message["language_code"]
    user["user_id"] = message["user_id"]
    for key, value in user.items():
        print(f"{key}: {value}")

    return user

def prepare_data_to_create_telegram_chat(chat,add_info: dict,full)-> dict:    
    result = {}
    username = getattr(chat, "username", "")
    result["tg_chat_id"] = get_peer_id(chat)
    result["title"] = getattr(chat, "title")
    result["username"] = username[1:] if username.startswith("@") else username
    result["description"] = add_info["description"]
    result["peer_type"] = add_info["peer_type"]

    result["access_hash"] = getattr(chat, "access_hash", None)
    result["is_megagroup"] = bool(getattr(chat, "megagroup", False))
    result["is_broadcast"] = bool(getattr(chat, "broadcast", False))
    result["is_forum"] = bool(getattr(chat, "forum", False))
    result["is_verified"] = bool(getattr(chat, "verified", False))
    result["is_scam"] = bool(getattr(chat, "scam", False))
    result["is_fake"] = bool(getattr(chat, "fake", False))
    result["is_restricted"] = bool(getattr(chat, "restricted", False))

    fc = getattr(full, "full_chat", None)
    print("это  fc\n\n")
    for key,value in fc.__dict__.items():
        print(f"{key}: {value}")
    print("the end of fc \n\n")
    result["participants_count"] = getattr(fc, "participants_count", None)
    result["admins_count"] = getattr(fc, "admins_count", None)
    result["kicked_count"] = getattr(fc, "kicked_count", None)
    result["banned_count"] = getattr(fc, "banned_count", None)
    result["online_count"] = getattr(fc, "online_count", None)
    result["slowmode_seconds"] = getattr(fc, "slowmode_seconds", None)
    result["pinned_msg_id"] = getattr(fc, "pinned_msg_id", None)
    result["linked_chat_id"] = getattr(fc, "linked_chat_id", None)
    result["stickerset_id"] = getattr(getattr(fc, "stickerset", None), "id", None)
    result["invite_link"] = getattr(getattr(fc, "exported_invite", None), "link", None)
    result["available_reactions"] = None

    #result["photo_small_path"] = None
    #result["photo_big_path"] = None

    #result["synced_at"] = None
    #result["stats_synced_at"] = None

    for key, value in result.items():
        print(f"{key}: {value}")
    return result

    # возможно нужно будет больше добавить полей

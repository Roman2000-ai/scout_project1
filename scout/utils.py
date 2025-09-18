from email.message import EmailMessage
from typing import Union, Dict


def parse_message_from_telegram(event) -> dict:
    """ 
    собирает данные о сообщения из  объекта Event

    """

    result = {}
    message = event.message

    result["user_id"] = message.sender_id
    result["chat_id"] = message.chat_id
    result["message_id"] = message.id
    result["date"] = message.date
    result["text"] = message.text
    result["category"] = None
    result["is_service_request"] = None

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
    

def prepare_data_to_create_telefram_user(message: dict) -> dict:

    user = {}

    user["username"] = message["username"]
    user["first_name"] = message["first_name"]
    user["last_name"] = message["last_name"]
    user["is_bot"] = message["is_bot"]
    user["phone"] = message["phone"]
    user["language_code"] =message["language_code"]
    user["id"] = message["user_id"]

    return user

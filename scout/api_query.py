from openai import AsyncOpenAI
from typing import Union
from dotenv import load_dotenv
import os 
import json

load_dotenv()

API_KEY_OPENAI=os.getenv("API_KEY_OPENAI")

MODEL = os.getenv("MODEL_AI","gpt-4o")


SYSTEM_PROMPT = """
You are a message classifier.

You have a list of objects in the following format:
{"message_id": number, "is_service_request": null, "category": null, "text": "message text"}

Your task:
1. For each message, determine if it is a service request.
2. If yes, specify a category from the list.
3. If no, set category=null and is_service_request=false.

Category list:
- repair
- delivery
- cleaning
- design
- advertising
- development
- consultation
- transportation
- installation
- configuration

Response format: Strictly a JSON array of objects, without any explanations or text, in the same order.ы
"""



async def send_query_ai(messages: list[dict]) -> Union [list[dict],None]:
    client =AsyncOpenAI(api_key=API_KEY_OPENAI)
    str_messages = None 

    print("отправляю запрос на open ai")
    try:
        response =  await client.chat.completions.create(
            model=MODEL,
            messages =[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user","content":json.dumps(messages, ensure_ascii=False)}
            ],
        )


        if not response or not response.choices:
            print(" Пустой ответ от API")
            return None
        str_messages = response.choices[0].message.content

        messages = json.loads(str_messages)
        return messages
    except Exception as e:
        print(" Ошибка при запросе:", str(e))
        if str_messages is not None:
            print(" Сырой ответ модели:", str_messages)
       
        return None
    

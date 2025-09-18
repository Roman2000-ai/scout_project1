#from concurrent.futures import thread
#from telegram import create_client_telegram
#from message_queue import worker
#import threading
import asyncio
from fastapi import FastAPI,Depends
from typing import List
from db.crud import get_telegram_messages_by_category, get_messages_with_user_by_category_flat
from schemas import MessageWithUserFlat
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_fastapi_session
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI() 


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://0.0.0.0:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/categories/{category}",response_model=List[MessageWithUserFlat])
async def give_messages_from_gategory(category:str,limit:int=100,offset:int=0,session:AsyncSession = Depends(get_fastapi_session)):
    
    messages = await get_messages_with_user_by_category_flat(session=session,category=category,skip=offset,limit=limit)

    return messages







#if __name__ == "__main__":
#    t = threading.Thread(target=worker, daemon=True)
#    t.start()
#    # вопрос по поводу потоков почему  worker работает не как задумано
#    asyncio.run(create_client_telegram())
    


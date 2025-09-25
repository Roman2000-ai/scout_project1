#from concurrent.futures import thread
#from telegram import create_client_telegram
#from message_queue import worker
#import threading
import security
import asyncio
from fastapi import FastAPI,Depends,HTTPException, status
from typing import List
from db.crud import get_telegram_messages_by_category, get_messages_with_user_by_category_flat,get_chats_from_db,get_messages_by_id_chat_db,get_users_db,get_user_by_user_id_db,get_user_by_username,create_user, login_for_access_token
from schemas import MessageWithUserFlat,TelegramChatSchema,TelegramUserSchema,UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_fastapi_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from dependencies import get_current_user

app = FastAPI() 


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://0.0.0.0:5500",
        "http://0.0.0.0:5050",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/categories/{category}",response_model=List[MessageWithUserFlat])
async def give_messages_from_gategory(category:str,limit:int=100,offset:int=0,session:AsyncSession = Depends(get_fastapi_session),current_user_id:str= Depends(get_current_user)):
    
    messages = await get_messages_with_user_by_category_flat(session=session,category=category,skip=offset,limit=limit)

    return messages
# @app.get("/chats/",response_model=List[None])
# async def  give_list_chats():

#     chats  = await


@app.get("/chats/",response_model=List[TelegramChatSchema])
async def give_chats(limit:int =100, offset: int = 0,q:str= None,session:AsyncSession = Depends(get_fastapi_session),current_user_id:str= Depends(get_current_user)):
    chats = await get_chats_from_db(session=session,limit=limit, offset= offset,q=q)
    return chats

@app.get("/chats/{chat_id}",response_model=List[MessageWithUserFlat])
async def get_messages_by_id_chat(chat_id:int ,limit:int=100,offset:int=0,session:AsyncSession = Depends(get_fastapi_session),current_user_id:str= Depends(get_current_user)):
    messages = await get_messages_by_id_chat_db(session=session,chat_id=chat_id,offset=offset,limit=limit)
    return messages



@app.get("/users/",response_model=List[TelegramUserSchema])
async def get_users(offset:int=0,limit:int=100,session:AsyncSession = Depends(get_fastapi_session),current_user_id:str= Depends(get_current_user)):
    users = await get_users_db(session,offset=offset,limit =limit)
    return  users


@app.get("/users/{user_id}",response_model=List[TelegramUserSchema],)
async def get_user_by_user_id(user_id:int,session:AsyncSession = Depends(get_fastapi_session),current_user_id:str= Depends(get_current_user)):
    users = await get_user_by_user_id_db(session=session,user_id=user_id)
    return users

@app.post("/token/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session:AsyncSession = Depends(get_fastapi_session),
):
    success, user = await login_for_access_token(session,form_data)

    if  success:
        access_token = security.create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    else: 
          raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )

@app.post("/register/")
async def register(user_data: UserCreate,session:AsyncSession = Depends(get_fastapi_session)):


    user_db = await get_user_by_username(session,user_data)

    if user_db:
        raise HTTPException(
            status_code=400,
            detail="Имя пользователя уже занято"
        )
    new_user  = await create_user(session,user_data)
    access_token = security.create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


#if __name__ == "__main__":
#    t = threading.Thread(target=worker, daemon=True)
#    t.start()
#    # вопрос по поводу потоков почему  worker работает не как задумано
#    asyncio.run(create_client_telegram())
    


#from queue import Queue, Empty
import asyncio
import time
from utils import prepare_for_api_ai_request, add_message_data,prepare_data_to_create_telefram_user
from api_query import send_query_ai
from db.crud import create_telegram_message,create_or_update_user_telegram
from db.database import get_session






async def worker(q: asyncio.Queue):
    print("worker запущен")
    while True:
        print("идет цикл worker")
        batch = []
        start_time = time.time()

        while len(batch) < 50:
            print("сообщений меньше 50")
            try:
                
                item = await asyncio.wait_for(q.get(), timeout=10.0)
                batch.append(item)
                print(f"f сообщение добавлено в  batch {item['text']}")
            except asyncio.TimeoutError:
                print("очередь пустая")
                break

            if time.time()-start_time >10 :
                print("время одижидание превысило 10сек")

                break

        if batch:
            print("batch  не пустой ")
            messages_for_requests =  prepare_for_api_ai_request(batch)
            while True:
                try: 

                    print(messages_for_requests)
                    messages_with_category =  await send_query_ai(messages_for_requests)
                    if messages_with_category:
                        print(messages_with_category)
                    
                    
                    messages = add_message_data(batch,messages_with_category)
                    if messages:
                       
                        async with get_session() as session:
                            for message in messages:
                                try:
                                    await create_telegram_message(session=session, message=message)
                                    user = prepare_data_to_create_telefram_user(message=message)
                                    print(user)
                                    
                                    await create_or_update_user_telegram(session=session,user = user )
                                    print("create_telegram_message  отработала успешно")
                                except Exception as e:
                                    print(f"произошла ошибка в create_telegram_message error:{str(e)}")
                                
                        
                            
                            
                    else:
                        print("что то пошло нетак с добавлением  категорий в сообщение")
                        

                    
                    for _ in range(len(batch)):
                        q.task_done()
                    break


                except Exception as e:
                    print(e)
                   
                    print("повторная поптыка запроса")
                    await asyncio.sleep(10.0)
                    break
            





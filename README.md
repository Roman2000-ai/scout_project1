# Scout Project

Сервис для мониторинга Telegram (через **Telethon**), фильтрации/классификации сообщений и сохранения их в БД. Данные доступны через **FastAPI**.

---

## Возможности
- Авторизация в Telegram (user client: `api_id`/`api_hash`).
- Прослушивание чатов/каналов, фильтрация сообщений по правилам/категориям.
- Сохранение в БД (**SQLite** по умолчанию; легко переключить на PostgreSQL).
- REST API на **FastAPI**.
- Миграции БД через **Alembic** (инициализируются локально **в папке `db/alembic`**).

---

## Технологии
- Python 3.12+
- FastAPI, Uvicorn
- SQLAlchemy (+ Alembic)
- SQLite (`aiosqlite`) 
- Telethon
- python-dotenv

---

## Требования
- Создай виртуальное окружение и установи зависимости:
  ```bash
  python -m venv venv
  source venv/bin/activate           
  pip install -r requirements.txt    
  ```

- Создай файл **`.env`** (не коммитим):
  ```ini
  # Telegram (получить на https://my.telegram.org → API Development Tools)
  TELEGRAM_API_ID=123456
  TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  OPENAI_API_KEY=sk-...
  MODEL=model of openai
  NAME_CHAT=NAME_CHAT

 


  ```



---

## Alembic — инициализация **в папке `db`**



---

## Запуск: три терминала

### Терминал 1 — **Telegram клиент** (первый запуск спросит телефон и код один раз)
```bash
source venv/bin/activate
python telegram.py
```
- При первом запуске Telethon запросит **номер телефона** и **код подтверждения** из Telegram.
- После успешной авторизации появится файл сессии (например, `scout/my_session.session`), он в `.gitignore`.

### Терминал 2 — **API (FastAPI/Uvicorn)**
```bash
source venv/bin/activate
uvicorn main:app --reload -port 8000
# http://127.0.0.1:8000/
# Документация Swagger: http://127.0.0.1:8000/docs
```


### Терминал 3 — фронт (index.html)

Запускаем простой  хост из папки `front` и открываем страницу:

```bash
cd front
python -m http.server 5050   
# затем в браузере:
# http://localhost:5050/index.html

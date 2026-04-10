import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Подключаемся, используя переменные окружения
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS'),
    port=os.getenv('DB_PORT')
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'warriors_db'")
exists = cursor.fetchone()
if not exists:
    cursor.execute("CREATE DATABASE warriors_db")
    print("База данных 'warriors_db' создана.")
else:
    print("База данных 'warriors_db' уже существует.")

cursor.close()
conn.close()
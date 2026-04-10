import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="123456",
    port=5432
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
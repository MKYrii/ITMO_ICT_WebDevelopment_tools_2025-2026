import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        user="postgres",
        password="123456",
        dbname="postgres"
    )
    print("Подключение успешно!")
    conn.close()
except Exception as e:
    print("Ошибка:", repr(e))
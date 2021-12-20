import psycopg2
import os

def get_db_connection():
    user = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PW')

    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user=user,
        password=password)

    return conn
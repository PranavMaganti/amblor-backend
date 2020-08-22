import pymysql
import pymysql.cursors
import json

from modules.models import Track

with open("auth/cloud_sql.json", "r") as file:
    creds = json.loads(file.read())
    db_username: str = creds["user"]
    db_password: str = creds["password"]
    db_host: str = creds["host"]

connection = pymysql.connect(host=db_host,
                             user=db_username,
                             password=db_password,
                             db='amblor',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def insert_user(username: str, email: str) -> int:
    with connection.cursor() as cursor:
        sql = "INSERT INTO User (username, email) VALUES (%s, %s)"
        cursor.execute(sql, (username, email))
        connection.commit()
    return cursor.lastrowid
     

def is_user_new(email: str) -> bool:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchall()
    return not result
    
def is_username_taken(username: str) -> bool:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE username=%s"
        cursor.execute(sql, (username,))
        result = cursor.fetchall()
    return bool(result)

def get_user(email: str):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
    return result

def get_scrobbles(email: str):
    with connection.cursor() as cursor:
        with open("queries/select.sql", "r") as readfile:
            sql = ' '.join(readfile.read().split())
            cursor.execute(sql, (email,))
            result = cursor.fetchall()
    return result


def insert_scrobble(track: Track, email: str):
    pass
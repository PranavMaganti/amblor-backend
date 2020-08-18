import pymysql
import pymysql.cursors
import json

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
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO User (username, email) VALUES (%s, %s)"
            cursor.execute(sql, (username, email))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()    
        return -1         

def is_user_new(email: str) -> bool:
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM User WHERE email='%s'".format(email)
            cursor.execute(sql)
            result = cursor.fetchall()
            return not result
    finally:
        connection.close()      
        return False

def is_username_taken(username: str) -> bool:
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM User WHERE username='%s'".format(username)
            cursor.execute(sql)
            result = cursor.fetchall()
            return bool(result)
    finally:
        connection.close()      
        return True

def get_user(username: str):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM User WHERE username='%s'".format(username)
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()      
        return True
import os
import pymysql
from pymysql.cursors import DictCursor
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

def get_db():
    connection = None
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False
        )
        yield connection
    except pymysql.MySQLError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed database connection {str(e)}"
        )

    finally:
        if connection:
            connection.close()
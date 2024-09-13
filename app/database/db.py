import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

def execute_query(query, params=None):
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to establish database connection")
        return None

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.lastrowid
        return result
    except mysql.connector.Error as error:
        logger.error(f"Error executing query: {error}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

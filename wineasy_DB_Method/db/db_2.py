import mysql.connector
import os
from dotenv import load_dotenv
import re

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME')
    )


def is_korean(text):
    return bool(re.search('[\u3131-\uD79D]', text))

def get_wine_detail_by_name(wine_name):
    conn = None
    try:
        print("Connecting to the database...")
        conn = get_db_connection()
        print("Connected to the database.")
        
        cursor = conn.cursor()
        
        # 입력된 이름이 한글인지 영어인지 판별
        if is_korean(wine_name):
            query = "SELECT * FROM wine_detail WHERE wine_name_ko LIKE %s"
            params = (f"%{wine_name}%",)
        else:
            query = "SELECT * FROM wine_detail WHERE wine_name_en LIKE %s"
            params = (f"%{wine_name}%",)

        print(f"Executing query: {query} with parameter: {params}")

        cursor.execute(query, params)
        
        result = cursor.fetchall()
        print("Query executed successfully.")
        print(f"Number of rows fetched: {len(result)}")
        
        wine_details = [
            {
                'id': row[0],
                'wine_name_ko': row[1],
                'wine_name_en': row[2],
                'country': row[3],
                'recommended_dish': row[4],
                'taste': row[5],
                'wine_type': row[6],
                'wine_sweet': row[7],
                'wine_body': row[8],
                'wine_acidity': row[9],
                'wine_tannin': row[10]
            }
            for row in result
        ]
        print("Wine details processed successfully.")
        return wine_details
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


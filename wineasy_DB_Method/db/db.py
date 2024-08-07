import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME')
    )

def get_wine_detail_by_name(wine_name_en):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM wine_detail WHERE wine_name_en LIKE %s"
        cursor.execute(query, (f"%{wine_name_en}%",))
        result = cursor.fetchall()
        return [
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
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn:
            conn.close()
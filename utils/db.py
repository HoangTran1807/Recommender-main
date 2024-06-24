import pyodbc
import os

class DB:
    dataSource = os.getenv("DATABASE_URL")

    @staticmethod
    def get_from_db(query: str):
        conn = pyodbc.connect(DB.dataSource)
        cursor = conn.cursor()

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data

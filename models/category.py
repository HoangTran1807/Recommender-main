import os
import pyodbc

from utils.db import DB

class Category:

    def __init__(self, id: int):
        self.id = id

    @staticmethod
    def get_from_db():
        query = "SELECT Id FROM Category"
        rows = DB.get_from_db(query)
        categories: list[Category] = []
        for row in rows:
            category = Category(row[0])
            categories.append(category)

        return categories

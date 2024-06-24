import os
import pyodbc

from utils.db import DB


class Product:

    def __init__(self, id: int, name: str, tags = []):
        self.id = id
        self.name = name
        self.tags = tags

    @staticmethod
    def get_from_db():
        query = "SELECT Id, Name FROM Product"
        rows = DB.get_from_db(query)
        products: list[Product] = []
        for row in rows:
            product = Product(row[0], row[1])
            products.append(product)

        return products

import os
import pyodbc

from utils.db import DB


class Comment:

    def __init__(self, productId: int, userId: int, rating: int, date: str, content: str):
        self.productId = productId
        self.userId = userId
        self.rating = rating
        self.date = date
        self.content = content

    @staticmethod
    def get_from_db():
        query = "SELECT ProductId, UserId, Rating, [Date], Content FROM Comment"
        rows = DB.get_from_db(query)
        comments: list[Comment] = []
        for row in rows:
            comment = Comment(row[0], row[1], row[2], row[3], row[4])
            comments.append(comment)

        return comments

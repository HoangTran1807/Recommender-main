from utils.db import DB


class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    @staticmethod
    def get_from_db():
        query = "SELECT Id, Name FROM People"
        rows = DB.get_from_db(query)
        users: list[User] = []
        for row in rows:
            user = User(row[0], row[1])
            users.append(user)

        return users

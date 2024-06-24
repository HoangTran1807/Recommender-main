from datetime import datetime


class UserAction:
    def __init__(
        self,
        day: datetime,
        star: int,
        user_id: int,
        product_id: int,
    ):
        self.day = day
        self.star = star
        self.user_id = user_id
        self.product_id = product_id

    def __str__(self):
        return f"{self.day}, {self.star}, {self.user_id}, {self.product_id}"

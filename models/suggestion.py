class Suggestion:
    def __init__(self, userId, productId, rating):
        self.user_id = userId
        self.product_id = productId
        self.rating = rating

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
        }

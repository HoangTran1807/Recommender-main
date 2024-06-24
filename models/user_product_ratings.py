class UserProductRatings:
    def __init__(self, user_id, products_count):
        self.user_id = user_id
        self.product_ratings = [0.0] * products_count
        self.Score = 0.0

    def append_ratings(self, ratings):
        self.product_ratings.extend(ratings)

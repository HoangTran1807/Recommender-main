class SvdResult:
    def __init__(
        self,
        average_global_rating,
        user_biases,
        product_biases,
        user_features,
        product_features,
    ):
        self.AverageGlobalRating = average_global_rating
        self.UserBiases = user_biases
        self.ProductBiases = product_biases
        self.UserFeatures = user_features
        self.ProductFeatures = product_features

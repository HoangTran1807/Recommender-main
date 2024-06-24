import math


class CosineComparer:
    @staticmethod
    def compare_vectors(user_features_one, user_features_two):
        sum_product = 0.0
        sum_one_squared = 0.0
        sum_two_squared = 0.0

        for i in range(len(user_features_one)):
            sum_product += user_features_one[i] * user_features_two[i]
            sum_one_squared += user_features_one[i] ** 2
            sum_two_squared += user_features_two[i] ** 2

        return sum_product / (math.sqrt(sum_one_squared) * math.sqrt(sum_two_squared))

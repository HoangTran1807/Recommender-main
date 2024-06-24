import random
import math

from models.svd_result import SvdResult

class SingularValueDecomposition:
    def __init__(self, features=20, iterations=100, learning_speed=0.005):
        self.numFeatures = features
        self.learningIterations = iterations
        self.learningRate = learning_speed
        self.learningDescent = 0.99
        self.regularizationTerm = 0.02

    def initialize(self, ratings):
        self.numUsers = len(ratings.Users)
        self.numArticles = len(ratings.Users[0].product_ratings)

        rand = random.Random()

        self.userFeatures = [
            [rand.random() for _ in range(self.numFeatures)]
            for _ in range(self.numUsers)
        ]
        self.articleFeatures = [
            [rand.random() for _ in range(self.numFeatures)]
            for _ in range(self.numArticles)
        ]
        self.userBiases = [0.0] * self.numUsers
        self.articleBiases = [0.0] * self.numArticles

    def factorize_matrix(self, ratings):
        self.initialize(ratings)

        average_global_rating = self.get_average_rating(ratings)

        rmse_all = []

        squared_error = 0.0
        i = 0
        while i < self.learningIterations:
            # while i < self.learningIterations or squared_error > self.min_squared_error:
            squared_error = 0.0
            count = 0

            for userIndex in range(self.numUsers):
                for articleIndex in range(self.numArticles):
                    if ratings.Users[userIndex].product_ratings[articleIndex] != 0:
                        predicted_rating = (
                            average_global_rating
                            + self.userBiases[userIndex]
                            + self.articleBiases[articleIndex]
                            + self.get_dot_product(
                                self.userFeatures[userIndex],
                                self.articleFeatures[articleIndex],
                            )
                        )

                        error = (
                            ratings.Users[userIndex].product_ratings[articleIndex]
                            - predicted_rating
                        )

                        if math.isnan(predicted_rating):
                            raise Exception(
                                "Encountered a non-number while factorizing a matrix! Try decreasing the learning rate."
                            )

                        squared_error += error**2
                        count += 1

                        average_global_rating += self.learningRate * (
                            error - self.regularizationTerm * average_global_rating
                        )
                        self.userBiases[userIndex] += self.learningRate * (
                            error - self.regularizationTerm * self.userBiases[userIndex]
                        )
                        self.articleBiases[articleIndex] += self.learningRate * (
                            error
                            - self.regularizationTerm * self.articleBiases[articleIndex]
                        )

                        for featureIndex in range(self.numFeatures):
                            self.userFeatures[userIndex][
                                featureIndex
                            ] += self.learningRate * (
                                error * self.articleFeatures[articleIndex][featureIndex]
                                - self.regularizationTerm
                                * self.userFeatures[userIndex][featureIndex]
                            )
                            self.articleFeatures[articleIndex][
                                featureIndex
                            ] += self.learningRate * (
                                error * self.userFeatures[userIndex][featureIndex]
                                - self.regularizationTerm
                                * self.articleFeatures[articleIndex][featureIndex]
                            )

            squared_error = math.sqrt(squared_error / count)
            rmse_all.append(squared_error)

            if (i + 1) % 10 == 0:
                print("Iteration: %d ; error = %.4f" % (i + 1, squared_error))
            self.learningRate *= self.learningDescent
            i += 1

        return SvdResult(
            average_global_rating,
            self.userBiases,
            self.articleBiases,
            self.userFeatures,
            self.articleFeatures,
        )

    def get_average_rating(self, ratings):
        sum_ratings = 0.0
        count = 0

        for userIndex in range(self.numUsers):
            for articleIndex in range(self.numArticles):
                if ratings.Users[userIndex].product_ratings[articleIndex] != 0:
                    sum_ratings += ratings.Users[userIndex].product_ratings[
                        articleIndex
                    ]
                    count += 1

        return sum_ratings / count

    @staticmethod
    def get_dot_product(vector1, vector2):
        return sum(x * y for x, y in zip(vector1, vector2))

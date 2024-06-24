from matplotlib.pyplot import bar_label
import numpy as np
from models.linear_rater import LinearRater
from models.product import Product
from models.product_tag import ProductTag
from models.product_tag_counts import ProductTagCounts
from models.suggestion import Suggestion
from models.tag import Tag
from models.user import User
import numpy as np
import os
import numpy as np
import numpy as np
from collections import defaultdict
import pickle
from models.user_action import UserAction
from models.user_action_tag import UserActionTag
from models.user_product_ratings import UserProductRatings
from models.user_product_ratings_table import UserProductRatingsTable
from utils.cosine_comparer import CosineComparer
from utils.db import DB
from utils.singular_value_decomposition import SingularValueDecomposition
import numpy as np
from numpy.linalg import norm

from collections import Counter
from operator import itemgetter

class CollaborativeRecommenderSystemDatabase:
    def __init__(self):
        self.tags: list[Tag] = []
        self.products: list[Product] = []
        self.users: list[User] = []
        self.user_actions: list[UserAction] = []

    def get_product_tag_linking_table(self):
        product_tags = []
        for product in self.products:
            for tag in product.tags:
                product_tags.append(ProductTag(product.id, tag.id))
        return product_tags

    def clone(self):
        return pickle.loads(pickle.dumps(self))


class CollaborativeRecommenderSystemTransformer:
    def __init__(self, database):
        self.db = database

    def get_user_product_ratings_table(self, rater):
        table = UserProductRatingsTable()

        table.user_index_to_id = sorted(set(user.id for user in self.db.users))
        table.product_index_to_id = sorted(
            set(product.id for product in self.db.products)
        )

        for userId in table.user_index_to_id:
            table.Users.append(
                UserProductRatings(userId, len(table.product_index_to_id))
            )

            # Tạo một dict để lưu trữ dữ liệu đã nhóm
        grouped_data = defaultdict(list)

        # Nhóm các phần tử trong db.user_actions theo cặp (user_id, product_id)
        for action in self.db.user_actions:
            grouped_data[(action.user_id, action.product_id)].append(action)

        # Tính toán rating cho mỗi nhóm và lưu trữ kết quả vào một danh sách
        userProductRatingGroup = []
        for key, actions in grouped_data.items():
            rating = rater.get_rating(actions)
            userProductRatingGroup.append(
                {"user_id": key[0], "product_id": key[1], "rating": rating}
            )

        for userAction in userProductRatingGroup:
            userIndex = table.user_index_to_id.index(userAction["user_id"])
            productIndex = table.product_index_to_id.index(userAction["product_id"])

            table.Users[userIndex].product_ratings[productIndex] = userAction["rating"]

        return table

    def get_product_tag_counts(self):
        articleTags = []

        for article in self.db.products:
            articleTag = ProductTagCounts(article.product_id, len(self.db.tags))

            for tag in self.db.tags:
                articleTag.TagCounts[tag.TagID] = (
                    1.0 if any(x.Name == tag.Name for x in article.Tags) else 0.0
                )

            articleTags.append(articleTag)

        return articleTags

    def get_user_tags(self):
        userData = []
        articleTags = self.db.get_product_tag_linking_table()
        numFeatures = len(self.db.tags)

        userActionTags = (
            self.db.user_actions.join(
                articleTags, lambda u, t: u.product_id == t.product_id
            )
            .group_by(lambda x: (x.user_id, x.TagName))
            .select(
                lambda g: {"user_id": g[0][0], "TagName": g[0][1], "Count": len(g[1])}
            )
            .order_by(lambda x: (x.user_id, x.TagName))
            .to_list()
        )

        totalUserActions = len(userActionTags)
        lastFoundIndex = 0

        for user in self.db.users:
            uat = UserActionTag(user.id, numFeatures)

            dataCol = 0
            for tag in self.db.tags:
                tagActionCount = 0
                for i in range(lastFoundIndex, totalUserActions):
                    if (
                        userActionTags[i]["user_id"] == user.id
                        and userActionTags[i]["TagName"] == tag.Name
                    ):
                        lastFoundIndex = i
                        tagActionCount = userActionTags[i]["Count"]
                        break

                uat.action_tag_data[dataCol] = tagActionCount
                dataCol += 1

            # Normalize data to values between 0 and 5
            upperLimit = 5.0
            maxVal = max(uat.action_tag_data)
            if maxVal > 0:
                for i in range(len(uat.action_tag_data)):
                    uat.action_tag_data[i] = (
                        uat.action_tag_data[i] / maxVal
                    ) * upperLimit

            userData.append(uat)

        return userData


class CollaborativeFilterRecommender:
    def __init__(
        self, userComparer, implicitRater, numberOfNeighbors, latentFeatures=20
    ):
        self.comparer = userComparer
        self.rater = implicitRater
        self.neighborCount = numberOfNeighbors
        self.latentUserFeatureCount = latentFeatures
        self.ratings: UserProductRatingsTable

    def train(self, db):
        ubt = CollaborativeRecommenderSystemTransformer(db)
        self.ratings = ubt.get_user_product_ratings_table(self.rater)

        if self.latentUserFeatureCount > 0:
            svd = SingularValueDecomposition(self.latentUserFeatureCount, 100)
            results = svd.factorize_matrix(self.ratings)
            self.ratings.append_user_features(results.UserFeatures)

    def get_rating(self, userId, productId):
        user = next((x for x in self.ratings.Users if x.user_id == userId), None)
        if not user:
            return None

        neighbors = self.get_nearest_neighbors(user, self.neighborCount)
        return self._get_rating(user, neighbors, productId)

    def _get_rating(self, user, neighbors, productId):
        productIndex = self.ratings.product_index_to_id.index(productId)

        nonZero = [x for x in user.product_ratings if x != 0]
        avgUserRating = np.mean(nonZero) if nonZero else 0.0

        score = 0.0
        count = 0
        for neighbor in neighbors:
            nonZeroRatings = [x for x in neighbor.product_ratings if x != 0]
            avgRating = np.mean(nonZeroRatings) if nonZeroRatings else 0.0

            if neighbor.product_ratings[productIndex] != 0:
                score += neighbor.product_ratings[productIndex] - avgRating
                count += 1

        if count > 0:
            score /= count
            score += avgUserRating

        return score

    def get_suggestions(self, userId, numSuggestions):
        userIndex = next(
            (i for i, x in enumerate(self.ratings.user_index_to_id) if x == userId),
            None,
        )
        if userIndex is None:
            user = UserProductRatings(0, 0)
        else:
            user = self.ratings.Users[userIndex]

        neighbors = self.get_nearest_neighbors(user, self.neighborCount)

        suggestions = []
        for productIndex, productId in enumerate(self.ratings.product_index_to_id):
            if user.product_ratings[productIndex] == 0:
                score = 0.0
                count = 0
                for neighbor in neighbors:
                    if neighbor.product_ratings[productIndex] != 0:
                        score += neighbor.product_ratings[productIndex] - (
                            (neighbors.index(neighbor) + 1.0) / 100.0
                        )
                        count += 1
                if count > 0:
                    score /= count

                if score > 0:
                    suggestions.append(Suggestion(userId, productId, score))

        suggestions.sort(key=lambda x: x.rating, reverse=True)
        return suggestions[:numSuggestions]

    def get_nearest_neighbors(self, user, numUsers):
        neighbors = []
        for otherUser in self.ratings.Users:
            if otherUser.user_id != user.user_id:
                otherUser.Score = np.dot(
                    otherUser.product_ratings, user.product_ratings
                ) / (norm(otherUser.product_ratings) * norm(user.product_ratings))
                neighbors.append(otherUser)

        neighbors.sort(key=lambda x: x.Score, reverse=True)
        return neighbors[:numUsers]


class MatrixFactorizationRecommender:
    def __init__(self, implicit_rater, features=20):
        self.num_features = features
        self.learning_iterations = 100
        self.rater = implicit_rater
        self.ratings: UserProductRatingsTable = UserProductRatingsTable()
        self.svd = None
        self.num_users = None
        self.num_products = None

    def train(self, db):
        ubt = CollaborativeRecommenderSystemTransformer(db)
        self.ratings = ubt.get_user_product_ratings_table(self.rater)

        factorizer = SingularValueDecomposition(
            self.num_features, self.learning_iterations
        )
        self.svd = factorizer.factorize_matrix(self.ratings)

        self.num_users = len(self.ratings.user_index_to_id)
        self.num_products = len(self.ratings.product_index_to_id)

    def get_rating(self, user_id, product_id):
        user_index = self.ratings.user_index_to_id.index(user_id)
        product_index = self.ratings.product_index_to_id.index(product_id)

        return self.get_rating_for_index(user_index, product_index)

    def get_rating_for_index(self, user_index, product_index):
        if self.svd is not None:
            return (
                self.svd.AverageGlobalRating
                + self.svd.UserBiases[user_index]
                + self.svd.ProductBiases[product_index]
                + np.dot(
                    self.svd.UserFeatures[user_index],
                    self.svd.ProductFeatures[product_index],
                )
            )

    def get_suggestions(self, user_id, num_suggestions):
        user_index = self.ratings.user_index_to_id.index(user_id)
        user = self.ratings.Users[user_index]
        suggestions = []

        for product_index in range(len(self.ratings.product_index_to_id)):
            if user.product_ratings[product_index] == 0:
                rating = self.get_rating_for_index(user_index, product_index)
                suggestions.append(
                    Suggestion(
                        user_id, self.ratings.product_index_to_id[product_index], rating
                    )
                )

        suggestions.sort(key=lambda x: x.rating, reverse=True)
        max_rating = max(suggestions, key=lambda x: x.rating).rating
        filtered_suggestions = list(
            filter(lambda x: x.rating >= max_rating - 1.2, suggestions)
        )
        
        if(num_suggestions != -1):
            return filtered_suggestions[:num_suggestions]
        else:
            return filtered_suggestions

class CollaborativeRecommenderStore:
    recommender: MatrixFactorizationRecommender | None = None
    saved_model = "./data/collaborative_recommender.dat"
    cates = []
    prods = []
    users = []
    comments = []

    @staticmethod
    def get_instance():
        if CollaborativeRecommenderStore.recommender is None:
            rate = LinearRater(-4, -3, 1, 3, 5)

            CollaborativeRecommenderStore.recommender = MatrixFactorizationRecommender(
                rate, 20
            )
            if os.path.exists(CollaborativeRecommenderStore.saved_model):
                print("Loading saved model")
                CollaborativeRecommenderStore.recommender = (
                    CollaborativeRecommenderStore.load(
                        CollaborativeRecommenderStore.saved_model
                    )
                )
            else:
                print("Error loading saved model")
                CollaborativeRecommenderStore.load_and_train()
                CollaborativeRecommenderStore.save(
                    CollaborativeRecommenderStore.saved_model
                )

        return CollaborativeRecommenderStore.recommender

    @staticmethod
    def load_and_train():
        db = CollaborativeRecommenderStore.parser()
        if CollaborativeRecommenderStore.recommender is not None:
            CollaborativeRecommenderStore.recommender.train(db)

    @staticmethod
    def parser():
        cates = DB.get_from_db("SELECT Id FROM Category")
        prods = DB.get_from_db(
            """SELECT Id, 
                                    Name, 
                                    STRING_AGG(pc.[CategoryId], ',') WITHIN GROUP (ORDER BY pc.[CategoryId]) as Categories 
                                FROM Product
                                LEFT JOIN  ProductCategory pc ON Id = pc.[ProductId]
                                GROUP BY Id, Name"""
        )
        users = DB.get_from_db("SELECT Id, Name FROM People")
        comments = DB.get_from_db("SELECT * FROM Comment")

        db = CollaborativeRecommenderSystemDatabase()

        for cate in cates:
            db.tags.append(Tag(str(cate.Id)))

        for prod in prods:
            tags = []
            prod_tags = prod.Categories.split(",")
            for tag in prod_tags:
                tags.append(Tag(str(tag)))
            db.products.append(Product(prod.Id, prod.Name, tags))

        db.users.append(User(0, "Unknown"))
        for user in users:
            db.users.append(User(user.Id, user.Name))

        for comment in comments:
            db.user_actions.append(
                UserAction(
                    comment.Date, comment.Rating, comment.UserId, comment.ProductId
                )
            )

        return db

    @staticmethod
    def save(filename):
        pickle.dump(CollaborativeRecommenderStore.recommender, open(filename, "wb"))

    @staticmethod
    def load(filename):
        return pickle.load(open(filename, "rb"))

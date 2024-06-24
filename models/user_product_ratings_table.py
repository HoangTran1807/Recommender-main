from models.user_product_ratings import UserProductRatings
from PIL import Image

class UserProductRatingsTable:
    def __init__(self):
        self.Users = []
        self.user_index_to_id = []
        self.product_index_to_id = []

    def append_user_features(self, userFeatures):
        for i in range(len(self.user_index_to_id)):
            self.Users[i].append_ratings(userFeatures[i])

    def append_product_features(self, productFeatures):
        for f in range(len(productFeatures[0])):
            newFeature = UserProductRatings(float("inf"), len(self.product_index_to_id))

            for a in range(len(self.product_index_to_id)):
                newFeature.product_ratings[a] = productFeatures[a][f]

            self.Users.append(newFeature)

    def save_sparcity_visual(self, file):
        minRating = min([min(user.product_ratings) for user in self.Users])
        maxRating = max([max(user.product_ratings) for user in self.Users])

        b = Image.new(
            "RGB", (len(self.product_index_to_id), len(self.user_index_to_id))
        )
        numPixels = 0

        for x in range(len(self.product_index_to_id)):
            for y in range(len(self.user_index_to_id)):
                brightness = 255 if self.Users[y].product_ratings[x] == 0 else 0
                b.putpixel((x, y), (brightness, brightness, brightness))

                numPixels += 1 if self.Users[y].product_ratings[x] != 0 else 0

        sparcity = numPixels / (
            len(self.product_index_to_id) * len(self.user_index_to_id)
        )
        b.save(file)

    def save_user_rating_distribution(self, file):
        bucketSize = 4
        maxRatings = max(
            [
                sum(1 for rating in user.product_ratings if rating != 0)
                for user in self.Users
            ]
        )
        buckets = [0] * int(maxRatings / bucketSize)

        for user in self.Users:
            ratingCount = sum(1 for rating in user.product_ratings if rating != 0)
            buckets[int(ratingCount / bucketSize)] += 1

        with open(file, "w") as w:
            w.write("numProductsRead,numUsers\n")
            for i, count in enumerate(buckets):
                w.write(f'="{i * bucketSize}-{((i + 1) * bucketSize) - 1}",{count}\n')

    def save_product_rating_distribution(self, file):
        bucketSize = 2
        maxRatings = 3000
        buckets = [0] * int(maxRatings / bucketSize)

        for i in range(len(self.product_index_to_id)):
            readers = sum(1 for user in self.Users if user.product_ratings[i] != 0)
            buckets[int(readers / bucketSize)] += 1

        while buckets[-1] == 0:
            buckets.pop()

        with open(file, "w") as w:
            w.write("numReaders,numProducts\n")
            for i, count in enumerate(buckets):
                w.write(f'="{i * bucketSize}-{((i + 1) * bucketSize) - 1}",{count}\n')

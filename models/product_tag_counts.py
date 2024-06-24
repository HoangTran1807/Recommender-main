class ProductTagCounts:
    def __init__(self, product_id, num_tags):
        self.product_id = product_id
        self.TagCounts = [0.0] * num_tags

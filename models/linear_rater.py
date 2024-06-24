from models.user_action import UserAction


class LinearRater:
    def __init__(
        self,
        one_star_weight=-5.0,
        two_star_weight=-3.0,
        three_star_weight=1.0,
        four_star_weight=3.0,
        five_star_weight=0.5,
        max_weight=5.0,
    ):
        self.one_star_weight = one_star_weight
        self.two_star_weight = two_star_weight
        self.three_star_weight = three_star_weight
        self.four_star_weight = four_star_weight
        self.five_star_weight = five_star_weight
        self.min_weight = 0.1
        self.max_weight = max_weight

    def get_rating(self, actions: list[UserAction]) -> float:
        one_star = sum(1 for action in actions if action.star == 1)
        two_star = sum(1 for action in actions if action.star == 2)
        three_star = sum(1 for action in actions if action.star == 3)
        four_star = sum(1 for action in actions if action.star == 4)
        five_star = sum(1 for action in actions if action.star == 5)

        rating = (
            one_star * self.one_star_weight
            + two_star * self.two_star_weight
            + three_star * self.three_star_weight
            + four_star * self.four_star_weight
            + five_star * self.five_star_weight
        )

        return min(self.max_weight, max(self.min_weight, rating))

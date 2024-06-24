class UserActionTag:
    def __init__(self, user_id, action_tag_count):
        self.user_id = user_id
        self.action_tag_data = [0.0] * action_tag_count
        self.Score = 0.0

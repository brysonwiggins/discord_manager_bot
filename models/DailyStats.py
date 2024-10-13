class DailyStats:
    def __init__(self, userId, data):
        self.userId = userId
        self.data = data if data is None else data.__dict__
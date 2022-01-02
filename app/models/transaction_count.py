from datetime import datetime

class Transaction_Count():
    def __init__(self, dt: datetime, count):
        self.timestamp = str(dt)
        self.count = count

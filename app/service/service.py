# could keep logic for object preparation
# right now it's quite dumb
class MemeOracleService:
    def __init__(self, storage, db):
        self.storage = storage
        self.db = db

    def get_random_object(self):
        return self.storage.get_random_object()

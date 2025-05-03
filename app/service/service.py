class MemeOracleService:
    def __init__(self, storage, db):
        self.storage = storage
        self.db = db

    def get_db_item_id(self, user_id: str):
        pass

    def get_random_object(self):
        return self.storage.get_random_object()

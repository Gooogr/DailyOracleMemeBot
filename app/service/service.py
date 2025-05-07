class MemeOracleService:
    def __init__(self, storage, db):
        self.storage = storage
        self.db = db

    def get_db_item_id(self, user_id: str):
        # implement logic of item selection based on interaction history/time/etc in db
        pass

    def get_object(self, item_id: str):
        return self.storage.get_object(object_id=item_id)

    def get_random_object(self):
        return self.storage.get_random_object()

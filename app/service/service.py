# could keep logic for object preparation
# right now it's quite dumb
class MemeOracleService:
    def __init__(self, storage):
        self.storage = storage

    def get_object(self):
        return self.storage.get_random_object()

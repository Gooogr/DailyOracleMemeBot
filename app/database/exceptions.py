class DatabaseError(Exception):
    """Generic database operation failure."""


class ItemNotFoundError(DatabaseError):
    def __init__(self, item_id: str):
        super().__init__(f"Item '{item_id}' not found.")
        self.item_id = item_id


class InteractionNotFoundError(DatabaseError):
    def __init__(self, user_id: int):
        super().__init__(f"No interactions found for user {user_id}.")
        self.user_id = user_id


class ItemAlreadyExistsError(DatabaseError):
    def __init__(self, item_id: str):
        super().__init__(f"Item '{item_id}' already exists.")
        self.item_id = item_id


class DatabaseConnectionError(DatabaseError):
    def __init__(self):
        super().__init__("Failed to connect to database.")

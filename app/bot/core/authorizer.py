import os


class Authorizer:
    env_key = "AUTHORIZED_TESTERS_TG_IDS"

    def __init__(self) -> None:
        self.allowed_ids = self._parse_env(self.env_key)

    @staticmethod
    def _parse_env(env_var: str) -> set:
        raw = os.getenv(env_var, "")
        return set(map(int, raw.split(","))) if raw else set()

    def is_tester(self, user_id: int) -> bool:
        return user_id in self.allowed_ids

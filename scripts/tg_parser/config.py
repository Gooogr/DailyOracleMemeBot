import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Config(BaseModel):
    api_id: int = Field(..., alias="API_ID")
    api_hash: str = Field(..., alias="API_HASH")
    channel_id: str = Field(..., alias="CHANNEL_ID")
    invite_link: str = Field(..., alias="INVITE_LINK")


def load_config(env_path: str = "scripts/tg_parser/.env") -> Config:
    load_dotenv(env_path)
    cfg = Config(**os.environ)
    return cfg

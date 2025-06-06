from io import BytesIO
from datetime import datetime, timezone
from unittest.mock import MagicMock
import os
import sys
from pathlib import Path
from types import ModuleType
from dataclasses import dataclass

import pytest

sys.modules.setdefault("telebot", MagicMock())
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

fake_models = ModuleType("app.database.models")

@dataclass
class Item:
    id: str
    s3_name: str
    type: str
    upload_dt: datetime | None = None

fake_models.Item = Item
sys.modules.setdefault("app.database.models", fake_models)

fake_facade = ModuleType("app.service.facade")

class MemeOracleService:
    pass

fake_facade.MemeOracleService = MemeOracleService
sys.modules.setdefault("app.service.facade", fake_facade)

from app.bot.bot import MemeOracleBot


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("AUTHORIZED_TESTERS_TG_IDS", raising=False)


@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def bot_mock():
    bot = MagicMock()
    bot.send_photo = MagicMock()
    bot.send_video = MagicMock()
    bot.reply_to = MagicMock()
    return bot


def make_item(item_type="image"):
    return Item(id="1", s3_name="name", type=item_type, upload_dt=datetime.now(timezone.utc))


def test_help_sends_instructions(service_mock, bot_mock):
    bot = MemeOracleBot(service_mock, token="t", bot=bot_mock)
    message = MagicMock()

    bot.help(message)

    bot_mock.reply_to.assert_called_once_with(message, "Ask the Oracle by using `/ask_oracle`.")


def test_random_requires_tester(monkeypatch, service_mock, bot_mock):
    monkeypatch.setenv("AUTHORIZED_TESTERS_TG_IDS", "42")
    message = MagicMock()
    message.from_user.id = 99

    bot = MemeOracleBot(service_mock, token="t", bot=bot_mock)
    bot.random(message)

    bot_mock.reply_to.assert_called_once_with(message, "Unknown command.")
    bot_mock.send_photo.assert_not_called()


def test_ask_oracle_sends_item_and_logs(service_mock, bot_mock):
    message = MagicMock()
    message.chat.id = 5
    message.from_user.id = 7

    item = make_item()
    service_mock.get_candidate_items.return_value = [item]
    service_mock.get_object.return_value = BytesIO(b"data")

    bot = MemeOracleBot(service_mock, token="t", bot=bot_mock)
    bot.ask_oracle(message)

    bot_mock.send_photo.assert_called_once_with(message.chat.id, service_mock.get_object.return_value)
    service_mock.log_interaction.assert_called_once_with(7, item.id)

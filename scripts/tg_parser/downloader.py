import os
from datetime import datetime

from config import Config
from pyrogram import Client


class TelegramMediaDownloader:
    def __init__(
        self,
        cfg: Config,
        client: Client,
        start_date: datetime,
        end_date: datetime,
        save_dir: str,
    ):
        self.cfg = cfg
        self.client = client
        self.start_date = start_date
        self.end_date = end_date
        self.save_dir = save_dir

    def run(self):
        self.client.run(self._process_channel())

    async def _process_channel(self):
        print(f"📅 Selected time range [{self.start_date} ... {self.end_date}]")
        os.makedirs(self.save_dir, exist_ok=True)

        await self._peer_channel()
        await self._download_channel_media()

        print("✅ Done!")

    async def _peer_channel(self):
        try:
            chat = await self.client.get_chat(self.cfg.invite_link)
            print(f"Resolved channel: {chat.title} (id: {chat.id})")
        except Exception as e:
            raise ValueError(f"Could not resolve chat from invite: {e}") from e

    async def _download_channel_media(self):
        count = 0
        async for msg in self.client.get_chat_history(self.cfg.channel_id):
            if msg.date < self.start_date:
                break
            if self.start_date <= msg.date <= self.end_date and (msg.photo or msg.video):
                filename = self._generate_filename(msg)
                filepath = os.path.join(self.save_dir, filename)
                try:
                    await self.client.download_media(msg, file_name=filepath)
                    count += 1
                    print(f"💾 Saved file #{count}: {filepath}")
                except Exception as e:  # pylint: disable=W0718
                    print(f"⚠️ Error downloading file to {filepath}: {e}")

    @staticmethod
    def _generate_filename(msg) -> str:
        date_str = msg.date.strftime("%Y-%m-%d_%H-%M-%S")
        ext = ".jpg" if msg.photo else ".mp4"
        return f"{date_str}{ext}"

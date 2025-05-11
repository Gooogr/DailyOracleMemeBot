import argparse
import os
from datetime import datetime, timedelta

from config import Config, load_config
from pyrogram import Client


class TelegramMediaDownloader:
    def __init__(
        self,
        cfg: Config,
        start_date: datetime,
        end_date: datetime,
        save_dir: str = "./data",
        session_name: str = "my_session",
    ):
        self.cfg = cfg
        self.start_date = start_date
        self.end_date = end_date
        self.save_dir = save_dir
        self.session_name = session_name

    def run(self):
        with Client(
            name=self.session_name,
            api_id=self.cfg.api_id,
            api_hash=self.cfg.api_hash,
        ) as client:
            client.run(self._process_channel(client))

    async def _process_channel(self, client):
        print(f"📅 Selected time range [{self.start_date} ... {self.end_date}]")
        os.makedirs(self.save_dir, exist_ok=True)

        await self._peer_channel(client)
        await self._download_channel_media(client)

        print("✅ All files were saved successfully.")

    async def _peer_channel(self, client: Client) -> None:
        try:
            chat = await client.get_chat(self.cfg.invite_link)
            print(f"Resolved channel: {chat.title} (id: {chat.id})")
        except Exception as e:
            raise ValueError(f"Could not resolve chat from invite: {e}")

    async def _download_channel_media(self, client: Client) -> None:
        count = 0
        async for msg in client.get_chat_history(self.cfg.channel_id):
            if msg.date < self.start_date:
                break
            if self.start_date <= msg.date <= self.end_date and (
                msg.photo or msg.video
            ):
                filename = self._generate_filename(msg)
                filepath = os.path.join(self.save_dir, filename)
                try:
                    await client.download_media(msg, file_name=filepath)
                    count += 1
                    print(f"💾 Saved file #{count}: {filepath}")
                except Exception as e:
                    print(f"⚠️ Error downloading file to {filepath}: {e}")

    @staticmethod
    def _generate_filename(msg) -> str:
        date_str = msg.date.strftime("%Y-%m-%d_%H-%M-%S")
        ext = ".jpg" if msg.photo else ".mp4"
        return f"{date_str}{ext}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Tg parser",
        description="Parse images and videos from private tg channel",
    )
    parser.add_argument(
        "-s", "--start-date", required=True, help="Start date YYYY-MM-DD"
    )
    parser.add_argument("-e", "--end-date", required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "-d", "--save-dir", default="./data", help="Directory to save media"
    )
    parser.add_argument(
        "-n", "--session-name", default="my_session", help="Pyrogram session name"
    )
    args = parser.parse_args()

    cfg = load_config()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = (
        datetime.strptime(args.end_date, "%Y-%m-%d")
        + timedelta(days=1)
        - timedelta(microseconds=1)
    )
    downloader = TelegramMediaDownloader(
        cfg=cfg,
        start_date=start_date,
        end_date=end_date,
        save_dir=args.save_dir,
        session_name=args.session_name,
    )
    downloader.run()

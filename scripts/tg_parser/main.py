import argparse
import asyncio
import os
from datetime import datetime, timedelta

from config import Config, load_config
from pyrogram import Client


async def resolve_channel(client: Client, invite_link: str) -> None:
    try:
        chat = await client.get_chat(invite_link)
        print(f"Resolved channel: {chat.title} (id: {chat.id})")
    except Exception as e:
        raise ValueError(f"Could not resolve chat from invite: {e}")


def generate_filename(msg) -> str:
    date_str = msg.date.strftime("%Y-%m-%d_%H-%M-%S")
    ext = ".jpg" if msg.photo else ".mp4"
    return f"{date_str}{ext}"


async def download_channel_media(
    client: Client,
    cfg: Config,
    start_date: datetime,
    end_date: datetime,
    save_dir: str,
) -> None:
    os.makedirs(save_dir, exist_ok=True)

    await resolve_channel(client, cfg.invite_link)
    count = 0

    async for msg in client.get_chat_history(cfg.channel_id):
        if msg.date < start_date:
            break
        if start_date <= msg.date <= end_date and (msg.photo or msg.video):
            filename = generate_filename(msg)
            filepath = os.path.join(save_dir, filename)
            result = await client.download_media(msg, file_name=filepath)
            if result and os.path.exists(result):
                count += 1
                print(f"✅ File #{count} saved: {filepath}")
            else:
                print(f"❌ Failed to save file: {filepath}")


async def run_downloader(
    cfg: Config,
    start_date: datetime,
    end_date: datetime,
    save_dir: str,
    session_name: str,
) -> None:
    print(f"Selected date range [{start_date} ... {end_date}]")

    async with Client(
        name=session_name, api_id=cfg.api_id, api_hash=cfg.api_hash
    ) as client:
        await download_channel_media(client, cfg, start_date, end_date, save_dir)
        print("🏁 Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Tg parser",
        description="Parse images and videos from private tg channel",
    )
    parser.add_argument("-s", "--start-date", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("-e", "--end-date", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("-d", "--save-dir", default="./data", help="Directory to save media")
    parser.add_argument("-n", "--session-name", default="my_session", help="Pyrogram session name")
    args = parser.parse_args()

    cfg = load_config()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(microseconds=1)

    asyncio.run(run_downloader(cfg, start_date, end_date, args.save_dir, args.session_name))

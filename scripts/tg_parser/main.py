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


async def main(
    cfg: Config,
    start_date: datetime,
    end_date: datetime,
    save_dir: str,
    session_name: str,
) -> None:
    os.makedirs(save_dir, exist_ok=True)

    print(f"Selected date range [{start_date} ... {end_date}]")

    async with Client(
        name=session_name, api_id=cfg.api_id, api_hash=cfg.api_hash
    ) as app:
        await resolve_channel(app, cfg.invite_link)

        count = 0
        async for msg in app.get_chat_history(cfg.channel_id):
            if msg.date < start_date:
                break  # История идёт в обратном порядке, можно остановиться
            if start_date <= msg.date < end_date + timedelta(days=1) and (
                msg.photo or msg.video
            ):
                count += 1
                filename = generate_filename(msg)
                filepath = os.path.join(save_dir, filename)
                result = await app.download_media(msg, file_name=filepath)
                if result and os.path.exists(result):
                    print(f"✅ File #{count} saved: {result}")
                else:
                    print(f"❌ Failed to save file: {filename}")

        print(f"🏁 Done. {count} files downloaded.")


if __name__ == "__main__":
    cfg = load_config()
    session_name = ("my_session",)
    parser = argparse.ArgumentParser(
        prog="Tg parser",
        description="Parse images and videos from private tg channel",
    )
    parser.add_argument(
        "-s", "--start-date", type=str, help="Start date in format YYYY-MM-DD"
    )
    parser.add_argument(
        "-e", "--end-date", type=str, help="End date in format YYYY-MM-DD"
    )
    parser.add_argument(
        "-d",
        "--save-dir",
        type=str,
        default="./data",
        help="Saving dir for parsed objects",
    )
    parser.add_argument(
        "-n",
        "--session-name",
        type=str,
        default="my_session",
        help="Path to pyrogram .session file",
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            cfg=cfg,
            start_date=datetime.strptime(args.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(args.end_date, "%Y-%m-%d"),
            save_dir=args.save_dir,
            session_name=args.session_name,
        )
    )

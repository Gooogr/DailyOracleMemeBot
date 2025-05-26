import argparse
from datetime import datetime, timedelta

from config import load_config
from downloader import TelegramMediaDownloader
from pyrogram import Client


def main():
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

    with Client(
        name=args.session_name,
        api_id=cfg.api_id,
        api_hash=cfg.api_hash,
    ) as client:
        downloader = TelegramMediaDownloader(
            cfg=cfg,
            client=client,
            start_date=start_date,
            end_date=end_date,
            save_dir=args.save_dir,
        )
        downloader.run()


if __name__ == "__main__":
    main()

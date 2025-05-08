import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client

load_dotenv("scripts/tg_parser/.env")

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_id = os.getenv("CHANNEL_ID")
invite_link = os.getenv("INVITE_LINK")

# Указываем даты в формате YYYY-MM-DD
START_DATE = datetime.strptime("2025-05-03", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-05-07", "%Y-%m-%d")

session_name = "my_session"
save_path = os.path.expanduser("~/Downloads/meme_media2")
os.makedirs(save_path, exist_ok=True)


async def main():
    async with Client(session_name, api_id=api_id, api_hash=api_hash) as app:
        print("📥 Client started. Ensuring access to the channel...")

        try:
            chat = await app.get_chat(invite_link)  # resolve from invite
            print(f"✅ Resolved channel: {chat.title} (id: {chat.id})")
        except Exception as e:
            print(f"❌ Could not resolve chat from invite: {e}")
            return

        count = 0
        async for msg in app.get_chat_history(channel_id):
            if msg.date < START_DATE:
                break  # История идёт в обратном порядке, можно остановиться
            if msg.date > END_DATE:
                continue

            if msg.photo or msg.video:
                count += 1
                date_str = msg.date.strftime("%Y-%m-%d_%H-%M-%S")
                ext = ".jpg" if msg.photo else ".mp4"
                filename = f"{date_str}{ext}"
                filepath = os.path.join(save_path, filename)

                result = await app.download_media(msg, file_name=filepath)
                if result and os.path.exists(result):
                    print(f"✅ File #{count} saved: {result}")
                else:
                    print(f"❌ Failed to save file: {filename}")

        print(f"🏁 Done. {count} files downloaded.")


if __name__ == "__main__":
    asyncio.run(main())

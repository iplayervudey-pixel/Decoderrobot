from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

app = Client(
    "bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

async def check_join(user_id):
    try:
        member = await app.get_chat_member(FORCE_CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            return True

        return False

    except:
        return False


@app.on_message(filters.command("start"))
async def start(client, message):

    joined = await check_join(message.from_user.id)

    if not joined:
        return await message.reply_text(
            "⚠️ Kamu harus join channel terlebih dahulu",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "JOIN CHANNEL",
                            url=CHANNEL_LINK
                        )
                    ]
                ]
            )
        )

    await message.reply_text(
        "✅ Kamu sudah join channel"
    )

app.run()

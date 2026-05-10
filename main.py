from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

app = Client(
    "forcejoinbot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)


async def is_joined(user_id):

    try:
        member = await app.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        print(member.status)

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            return True

        return False

    except Exception as e:
        print(e)
        return False


@app.on_message(filters.command("start"))
async def start_command(client, message):

    user_id = message.from_user.id

    joined = await is_joined(user_id)

    if not joined:

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "JOIN CHANNEL",
                        url=CHANNEL_LINK
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ SUDAH JOIN",
                        callback_data="check_join"
                    )
                ]
            ]
        )

        return await message.reply_text(
            "⚠️ Kamu harus join channel terlebih dahulu",
            reply_markup=buttons
        )

    await message.reply_text(
        "✅ Kamu sudah join channel"
    )


@app.on_callback_query(filters.regex("check_join"))
async def check_join_callback(client, query: CallbackQuery):

    user_id = query.from_user.id

    joined = await is_joined(user_id)

    if not joined:
        return await query.answer(
            "❌ Kamu belum join channel",
            show_alert=True
        )

    await query.message.edit_text(
        "✅ Join channel berhasil"
    )


print("BOT ONLINE")

app.run()

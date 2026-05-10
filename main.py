from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import UserNotParticipant

import os
import random
import string

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# CHANNEL FORCE SUBSCRIBE
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

# CHANNEL DATABASE
DB_CHANNEL = os.getenv("DB_CHANNEL")

app = Client(
    "memory_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True
)

user_uploads = {}
media_db = {}

# =========================
# CHECK JOIN CHANNEL
# =========================

async def check_join(client, user_id):

    try:

        member = await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        if member.status in [
            "member",
            "administrator",
            "owner",
            "restricted"
        ]:
            return True

    except UserNotParticipant:
        return False

    except:
        return False


# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message):

    joined = await check_join(
        client,
        message.from_user.id
    )

    if not joined:

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
                    )
                ]
            ]
        )

        return await message.reply_text(
            "⚠️ Silahkan gabung channel bot terlebih dahulu dan kembali lagi ke bot.",
            reply_markup=buttons
        )

    text = f"""
✅ Selamat datang di bot.

📤 Gunakan /upload untuk upload media
📥 Kirim code untuk download media

Commands:
/start
/upload
/download
/help
/myid
"""

    await message.reply_text(text)


# =========================
# HELP
# =========================

@app.on_message(filters.command("help"))
async def help_cmd(client, message):

    text = """
📖 Bantuan Bot

1. Join channel bot terlebih dahulu.
2. Gunakan bot dengan bijak.
3. Jangan spam upload media.
4. Dilarang upload file berbahaya.
5. Dilarang menyalahgunakan bot.
6. Share bot ke teman kalian.
7. Gunakan /upload untuk membuat code.
8. Kirim code untuk download media.

⚠️ Semua aktivitas tersimpan otomatis.
"""

    await message.reply_text(text)


# =========================
# MY ID
# =========================

@app.on_message(filters.command("myid"))
async def myid(client, message):

    await message.reply_text(
        f"🆔 ID Kamu:\n`{message.from_user.id}`"
    )


# =========================
# UPLOAD
# =========================

@app.on_message(filters.command("upload"))
async def upload(client, message):

    user_uploads[message.from_user.id] = []

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Tambah Media",
                    callback_data="add_media"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Buat Code",
                    callback_data="make_code"
                )
            ]
        ]
    )

    await message.reply_text(
        "📤 Silahkan kirim media lalu tekan tombol ✅ Buat Code jika selesai.",
        reply_markup=buttons
    )


# =========================
# SAVE MEDIA
# =========================

@app.on_message(filters.media)
async def save_media(client, message):

    user_id = message.from_user.id

    if user_id not in user_uploads:
        return

    copied = await message.copy(DB_CHANNEL)

    user_uploads[user_id].append(copied.id)

    await message.reply_text(
        f"✅ Media ditambahkan ({len(user_uploads[user_id])})"
    )


# =========================
# BUTTON CALLBACK
# =========================

@app.on_callback_query()
async def callbacks(client, callback_query):

    user_id = callback_query.from_user.id

    if callback_query.data == "add_media":

        await callback_query.answer(
            "Silahkan kirim media lagi"
        )


    elif callback_query.data == "make_code":

        media_ids = user_uploads.get(user_id, [])

        if not media_ids:

            return await callback_query.message.reply_text(
                "❌ Belum ada media"
            )

        code_random = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=10
            )
        )

        videos = 0
        photos = 0
        docs = 0

        for msg_id in media_ids:

            msg = await client.get_messages(
                DB_CHANNEL,
                msg_id
            )

            if msg.video:
                videos += 1

            elif msg.photo:
                photos += 1

            elif msg.document:
                docs += 1

        suffix = []

        if videos:
            suffix.append(f"{videos}V")

        if photos:
            suffix.append(f"{photos}P")

        if docs:
            suffix.append(f"{docs}B")

        suffix_text = "_".join(suffix)

        bot_username = (await client.get_me()).username

        final_code = f"{bot_username}:{code_random}_{suffix_text}"

        media_db[final_code] = media_ids

        del user_uploads[user_id]

        await callback_query.message.reply_text(
            f"✅ Code Berhasil Dibuat\n\n`{final_code}`"
        )


# =========================
# DOWNLOAD
# =========================

@app.on_message(filters.command("download"))
async def download(client, message):

    await message.reply_text(
        "📥 Silahkan kirim code terlebih dahulu"
    )


# =========================
# CODE DETECT
# =========================

@app.on_message(filters.text)
async def get_code(client, message):

    text = message.text.strip()

    if text in media_db:

        media_ids = media_db[text]

        for msg_id in media_ids:

            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=DB_CHANNEL,
                message_id=msg_id
            )


app.run()

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from pyrogram.errors import UserNotParticipant

import os
import random
import string

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")
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
# CHECK JOIN
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
# BOT COMMANDS
# =========================

@app.on_message(filters.command("setcmd"))
async def setcmd(client, message):

    commands = [
        BotCommand("start", "Mulai Bot"),
        BotCommand("upload", "Upload Media"),
        BotCommand("download", "Download Media"),
        BotCommand("help", "Bantuan"),
        BotCommand("myid", "ID Saya")
    ]

    await client.set_bot_commands(commands)

    await message.reply_text(
        "✅ Command bot berhasil dipasang"
    )


# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message):

    user_id = message.from_user.id

    joined = await check_join(client, user_id)

    # BELUM JOIN
    if not joined:

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Sudah Join",
                        callback_data="cek_join"
                    )
                ]
            ]
        )

        return await message.reply_text(
            "⚠️ Silahkan join channel bot terlebih dahulu untuk menggunakan semua fitur bot.",
            reply_markup=buttons
        )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📤 Upload",
                    callback_data="menu_upload"
                ),
                InlineKeyboardButton(
                    "📥 Download",
                    callback_data="menu_download"
                )
            ],
            [
                InlineKeyboardButton(
                    "🆘 Help",
                    callback_data="menu_help"
                ),
                InlineKeyboardButton(
                    "🆔 My ID",
                    callback_data="menu_myid"
                )
            ]
        ]
    )

    await message.reply_text(
        "✅ Verifikasi berhasil.

Silahkan gunakan bot dengan baik dan gunakan tombol di bawah untuk semua fitur bot.",
        reply_markup=buttons
    )


# =========================
# HELP
# =========================

@app.on_message(filters.command("help"))
async def help_cmd(client, message):

    text = """
📖 Bantuan Penggunaan Bot

1. Join channel bot terlebih dahulu.
2. Gunakan /upload untuk upload media.
3. Kirim banyak media sekaligus.
4. Tekan tombol ✅ Buat Code jika selesai upload.
5. Bot otomatis membuat code media.
6. Share code ke teman kalian.
7. Tempel code untuk download media.
8. Semua media tersimpan otomatis.

⚠️ Peraturan Bot:
- Jangan spam bot
- Jangan upload file berbahaya
- Jangan menyalahgunakan bot
- Gunakan dengan bijak
- Share bot ke teman kalian

Terima kasih telah menggunakan bot.
"""

    await message.reply_text(text)


# =========================
# MY ID
# =========================

@app.on_message(filters.command("myid"))
async def myid(client, message):

    await message.reply_text(
        f"🆔 ID Kamu:
`{message.from_user.id}`"
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
        "📤 Silahkan kirim media sekarang.

Jika sudah selesai upload tekan tombol ✅ Buat Code.",
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

    total = len(user_uploads[user_id])

    await message.reply_text(
        f"✅ Media berhasil ditambahkan

📦 Total media sekarang: {total}"
    )


# =========================
# CALLBACK BUTTONS
# =========================

@app.on_callback_query()
async def callbacks(client, callback_query):

    user_id = callback_query.from_user.id

    # =====================
    # CEK JOIN
    # =====================

    if callback_query.data == "cek_join":

        joined = await check_join(client, user_id)

        if joined:

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📤 Upload",
                            callback_data="menu_upload"
                        ),
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data="menu_download"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🆘 Help",
                            callback_data="menu_help"
                        ),
                        InlineKeyboardButton(
                            "🆔 My ID",
                            callback_data="menu_myid"
                        )
                    ]
                ]
            )

            return await callback_query.message.edit_text(
                "✅ Verifikasi berhasil.

Silahkan gunakan bot dengan baik.",
                reply_markup=buttons
            )

        return await callback_query.answer(
            "❌ Kamu belum join channel",
            show_alert=True
        )


    # =====================
    # MENU BUTTONS
    # =====================

    elif callback_query.data == "menu_upload":

        user_uploads[user_id] = []

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

        await callback_query.message.reply_text(
            "📤 Silahkan kirim media sekarang.",
            reply_markup=buttons
        )


    elif callback_query.data == "menu_download":

        await callback_query.message.reply_text(
            "📥 Silahkan kirim code media terlebih dahulu."
        )


    elif callback_query.data == "menu_help":

        await callback_query.message.reply_text(
            "📖 Gunakan /upload untuk membuat code dan kirim code untuk download media."
        )


    elif callback_query.data == "menu_myid":

        await callback_query.message.reply_text(
            f"🆔 ID Kamu:
`{user_id}`"
        )


    elif callback_query.data == "add_media":

        await callback_query.answer(
            "📤 Silahkan kirim media lagi"
        )


    # =====================
    # BUAT CODE
    # =====================

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
            f"✅ Code berhasil dibuat

🔑 Code:
`{final_code}`

📦 Total File: {len(media_ids)}"
        )


# =========================
# DOWNLOAD COMMAND
# =========================

@app.on_message(filters.command("download"))
async def download(client, message):

    await message.reply_text(
        "📥 Silahkan kirim code media sekarang."
    )


# =========================
# CODE DETECT
# =========================

@app.on_message(filters.text)
async def get_code(client, message):

    text = message.text.strip()

    if text not in media_db:
        return

    media_ids = media_db[text]

    total_media = len(media_ids)
    total_pages = (total_media + 9) // 10

    await message.reply_text(
        f"✅ Code ditemukan

📦 Total file: {total_media}
📄 Total halaman: {total_pages}

⬇️ Sedang menampilkan halaman pertama"
    )

    await send_page(
        client,
        message,
        media_ids,
        0,
        text
    )


# =========================
# SEND PAGE
# =========================

async def send_page(client, message, media_ids, page, code):

    start = page * 10
    end = start + 10

    current_media = media_ids[start:end]

    for msg_id in current_media:

        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=DB_CHANNEL,
            message_id=msg_id
        )

    total_pages = (len(media_ids) + 9) // 10

    buttons = []

    row = []

    if page > 0:

        row.append(
            InlineKeyboardButton(
                f"⬅️ Prev {page}",
                callback_data=f"page_{code}_{page-1}"
            )
        )

    if page < total_pages - 1:

        row.append(
            InlineKeyboardButton(
                f"Next {page+2} ➡️",
                callback_data=f"page_{code}_{page+1}"
            )
        )

    if row:
        buttons.append(row)

    if buttons:

        await message.reply_text(
            f"✅ Menampilkan halaman {page+1}/{total_pages}

📦 File {start+1}-{min(end, len(media_ids))}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# =========================
# PAGE CALLBACK
# =========================

@app.on_callback_query(filters.regex(r"^page_"))
async def page_callback(client, callback_query):

    data = callback_query.data.split("_")

    code = data[1]
    page = int(data[2])

    if code not in media_db:
        return

    media_ids = media_db[code]

    await callback_query.message.reply_text(
        f"📄 Membuka halaman {page+1}"
    )

    await send_page(
        client,
        callback_query.message,
        media_ids,
        page,
        code
    )


app.run()

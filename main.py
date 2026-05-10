from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)

import os
import random
import string
import asyncio
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

DB_FILE = "media_db.json"

# ================= LOAD DATABASE =================
try:
    with open(DB_FILE, "r") as f:
        media_db = json.load(f)
except:
    media_db = {}

# ================= BOT =================
app = Client(
    "memory_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True
)

user_uploads = {}

# ================= CHECK JOIN =================
async def check_join(client, user_id):

    try:
        member = await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        status = str(member.status).lower()

        return any(x in status for x in [
            "member",
            "administrator",
            "owner",
            "restricted"
        ])

    except:
        return False


# ================= MENU =================
def menu():

    return InlineKeyboardMarkup([
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
    ])


# ================= COMMAND =================
@app.on_message(filters.command("setcmd"))
async def setcmd(client, message):

    await client.set_bot_commands([
        BotCommand("start", "Mulai bot"),
        BotCommand("upload", "Upload media"),
        BotCommand("download", "Download media"),
        BotCommand("help", "Bantuan"),
        BotCommand("myid", "ID akun")
    ])

    await message.reply_text(
        "✅ Command berhasil dipasang"
    )


# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):

    user_id = message.from_user.id

    joined = await check_join(client, user_id)

    if not joined:

        return await message.reply_text(
            "⚠️ Anda harus join channel terlebih dahulu",
            reply_markup=InlineKeyboardMarkup([
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
            ])
        )

    await message.reply_text(
        """
✅ Verifikasi berhasil

Silahkan pilih menu dibawah
""",
        reply_markup=menu()
    )


# ================= HELP =================
@app.on_message(filters.command("help"))
async def help_cmd(client, message):

    text = """
<b>Cara Menggunakan Bot:</b>

1. Klik /upload
2. Kirim media
3. Klik tombol Done
4. Copy code
5. Kirim code untuk download file
"""

    await message.reply_text(
        text,
        parse_mode=enums.ParseMode.HTML
    )


# ================= MY ID =================
@app.on_message(filters.command("myid"))
async def myid(client, message):

    await message.reply_text(
        f"🆔 ID Anda:\n<code>{message.from_user.id}</code>",
        parse_mode=enums.ParseMode.HTML
    )


# ================= DOWNLOAD =================
@app.on_message(filters.command("download"))
async def download(client, message):

    await message.reply_text(
        """
📥 Silahkan kirim code media

Contoh:
<code>3V_5P_3B</code>
""",
        parse_mode=enums.ParseMode.HTML
    )


# ================= UPLOAD =================
@app.on_message(filters.command("upload"))
async def upload(client, message):

    user_uploads[message.from_user.id] = []

    await message.reply_text(
        """
📤 Mode upload aktif

Sekarang kirim media/video/file
""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Done",
                    callback_data="make_code"
                )
            ]
        ])
    )


# ================= SAVE MEDIA =================
@app.on_message(
    filters.photo |
    filters.video |
    filters.document |
    filters.audio |
    filters.animation
)
async def save_media(client, message):

    user_id = message.from_user.id

    if user_id not in user_uploads:
        return

    try:

        copied = await message.copy(DB_CHANNEL)

        user_uploads[user_id].append(copied.id)

        total = len(user_uploads[user_id])

        await message.reply_text(
            f"""
✅ Media berhasil disimpan

📦 Total media: {total}
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Buat Code",
                        callback_data="make_code"
                    )
                ]
            ])
        )

        await asyncio.sleep(1)

        try:
            await message.delete()
        except:
            pass

    except Exception as e:

        await message.reply_text(
            f"❌ Error\n<code>{e}</code>",
            parse_mode=enums.ParseMode.HTML
        )


# ================= CALLBACK =================
@app.on_callback_query()
async def callbacks(client, callback_query):

    await callback_query.answer()

    data = callback_query.data
    user_id = callback_query.from_user.id

    # ================= PAGE =================
    if data.startswith("page|"):

        _, code, page = data.split("|")

        page = int(page)

        if code not in media_db:

            return await callback_query.message.reply_text(
                "❌ Code tidak ditemukan"
            )

        return await send_page(
            client,
            callback_query.message,
            media_db[code],
            page,
            code
        )

    # ================= CHECK JOIN =================
    if data == "cek_join":

        joined = await check_join(client, user_id)

        if joined:

            return await callback_query.message.edit_text(
                """
✅ Verifikasi berhasil

Silahkan pilih menu dibawah
""",
                reply_markup=menu()
            )

        return await callback_query.answer(
            "❌ Anda belum join channel",
            show_alert=True
        )

    # ================= MENU UPLOAD =================
    elif data == "menu_upload":

        user_uploads[user_id] = []

        await callback_query.message.reply_text(
            """
📤 Mode upload aktif

Sekarang kirim media/video/file
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Done",
                        callback_data="make_code"
                    )
                ]
            ])
        )

    # ================= MENU DOWNLOAD =================
    elif data == "menu_download":

        await callback_query.message.reply_text(
            """
📥 Kirim code media

Contoh:
<code>3V_5P_3B</code>
""",
            parse_mode=enums.ParseMode.HTML
        )

    # ================= MENU HELP =================
    elif data == "menu_help":

        await callback_query.message.reply_text(
            """
<b>Cara Menggunakan:</b>

1. Upload media
2. Klik Done
3. Copy code
4. Kirim code
""",
            parse_mode=enums.ParseMode.HTML
        )

    # ================= MENU MYID =================
    elif data == "menu_myid":

        await callback_query.message.reply_text(
            f"<code>{user_id}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    # ================= MAKE CODE =================
    elif data == "make_code":

        media_ids = user_uploads.get(user_id, [])

        if not media_ids:

            return await callback_query.message.reply_text(
                "❌ Belum ada media"
            )

        # FORMAT CODE BARU
        code = "_".join([
            ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=2
            ))
            for _ in range(3)
        ])

        # PASTIKAN TIDAK DUPLIKAT
        while code in media_db:

            code = "_".join([
                ''.join(random.choices(
                    string.ascii_uppercase + string.digits,
                    k=2
                ))
                for _ in range(3)
            ])

        media_db[code] = media_ids

        with open(DB_FILE, "w") as f:
            json.dump(media_db, f)

        del user_uploads[user_id]

        await callback_query.message.reply_text(
            f"""
✅ Code berhasil dibuat

🔑 Code:
<code>{code}</code>

📥 Kirim code tersebut untuk download file
""",
            parse_mode=enums.ParseMode.HTML
        )


# ================= CODE DETECT =================
@app.on_message(filters.text)
async def get_code(client, message):

    text = message.text.strip()

    # BERSIHKAN SPASI
    text = text.replace(" ", "")

    found_code = None

    for saved_code in media_db.keys():

        if saved_code.lower() == text.lower():

            found_code = saved_code
            break

    if not found_code:
        return

    await send_page(
        client,
        message,
        media_db[found_code],
        0,
        found_code
    )


# ================= SEND PAGE =================
async def send_page(client, message, media_ids, page, code):

    per_page = 10

    start = page * per_page
    end = start + per_page

    current_ids = media_ids[start:end]

    total_pages = (
        len(media_ids) + per_page - 1
    ) // per_page

    # KIRIM MEDIA
    await client.copy_media_group(
        chat_id=message.chat.id,
        from_chat_id=DB_CHANNEL,
        message_ids=current_ids
    )

    buttons = []

    row = []

    for i in range(total_pages):

        row.append(
            InlineKeyboardButton(
                f"{'✅' if i == page else '☑️'} {i+1}",
                callback_data=f"page|{code}|{i}"
            )
        )

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    nav = []

    if page > 0:

        nav.append(
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"page|{code}|{page-1}"
            )
        )

    if page < total_pages - 1:

        nav.append(
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"page|{code}|{page+1}"
            )
        )

    if nav:
        buttons.append(nav)

    await message.reply_text(
        f"""
📂 Halaman: {page+1}/{total_pages}

📦 Total File: {len(media_ids)}

🔑 Code:
<code>{code}</code>
""",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


# ================= RUN =================
print("BOT RUNNING...")

app.run()

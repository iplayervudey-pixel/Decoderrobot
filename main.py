from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
    InputMediaAnimation
)
from pyrogram.errors import FloodWait

import os
import random
import string
import asyncio
import json

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")
DB_CHANNEL = os.getenv("DB_CHANNEL")

DB_FILE = "media_db.json"

# ================= LOAD DATABASE =================
try:
    with open(DB_FILE, "r") as f:
        media_db = json.load(f)
except:
    media_db = {}

if "views" not in media_db:
    media_db["views"] = {}

# ================= BOT =================
app = Client(
    "memory_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True
)

# ================= MEMORY =================
user_uploads = {}
upload_status_message = {}

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
                "Start🚀",
                callback_data="home"
            )
        ],

        [
            InlineKeyboardButton(
                "Trending Code🔥",
                callback_data="trend"
            ),

            InlineKeyboardButton(
                "New Code🆕",
                callback_data="new"
            )
        ],

        [
            InlineKeyboardButton(
                "My Code📂",
                callback_data="mycode"
            ),

            InlineKeyboardButton(
                "My Account🧑‍🏫",
                callback_data="account"
            )
        ],

        [
            InlineKeyboardButton(
                "Help📃",
                callback_data="help"
            ),

            InlineKeyboardButton(
                "Admin🧑‍💼",
                callback_data="admin"
            )
        ]

    ])


# ================= SET COMMAND =================
@app.on_message(filters.command("setcmd"))
async def setcmd(client, message):

    await client.set_bot_commands([
        BotCommand("start", "Mulai bot"),
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
Selamat Datang Di TZY BOT

Silakan Kirim Media Dan Saya Akan Memberimu Sebuah Code😉

Jika Ada Code Silahkan Kirim Ke Saya Dan Saya Memberi Mu Media Yang Menarik 😋
""",
        reply_markup=menu()
    )


# ================= HELP =================
@app.on_message(filters.command("help"))
async def help_cmd(client, message):

    await message.reply_text(
"""
<b>Cara Menggunakan Bot:</b>

1. Klik Start
2. Kirim media/file/video
3. Klik tombol Create
4. Copy code
5. Kirim code untuk download

Contoh:
<code>tzyfilebot_1v_0p_0d_xxxxx</code>
""",
        parse_mode=enums.ParseMode.HTML
    )


# ================= MY ID =================
@app.on_message(filters.command("myid"))
async def myid(client, message):

    await message.reply_text(
        f"""
🆔 ID Anda:

<code>{message.from_user.id}</code>
""",
        parse_mode=enums.ParseMode.HTML
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

        if user_id in upload_status_message:

            try:

                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=upload_status_message[user_id],
                    text=f"""
📤 MODE UPLOAD AKTIF

✅ Media berhasil disimpan

📦 Total media: {total}

Klik CREATE jika selesai upload
""",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "✅ Create",
                                callback_data="make_code"
                            )
                        ]
                    ])
                )

            except:
                pass

        try:
            await message.delete()
        except:
            pass

    except Exception as e:

        print(e)


# ================= CALLBACK =================
@app.on_callback_query()
async def callbacks(client, callback_query):

    await callback_query.answer()

    data = callback_query.data
    user_id = callback_query.from_user.id

    # ================= HOME =================
if data == "home":

    user_uploads[user_id] = []

    msg = await callback_query.message.edit_text(
"""
📥 MODE AKTIF

Silakan kirim media/video/file

📦 Total media diterima: 0

📌 Anda juga bisa tempel code
""",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "✅ Create",
                    callback_data="make_code"
                )
            ],

            [
                InlineKeyboardButton(
                    "🏠 Halaman Utama",
                    callback_data="start"
                )
            ]

        ])
    )

    upload_status_message[user_id] = msg.id

    # ================= CHECK JOIN =================
    elif data == "cek_join":

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

    # ================= NEW CODE =================
    elif data == "new":

        latest = [
            x for x in media_db.keys()
            if x != "views"
        ]

        latest.reverse()

        text = "🆕 NEW CODE\n\n"

        if not latest:

            text += "Belum ada code"

        else:

            for no, code in enumerate(latest[:20], start=1):

                text += (
                    f"{no}. "
                    f"<code>{code}</code>\n"
                )

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= TRENDING =================
    elif data == "trend":

        ranked = sorted(
            media_db["views"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        text = "🔥 TRENDING CODE\n\n"

        if not ranked:

            text += "Belum ada code trending"

        else:

            for no, (code, total) in enumerate(ranked[:20], start=1):

                text += (
                    f"{no}. "
                    f"<code>{code}</code>\n"
                    f"👁 Views: {total}\n\n"
                )

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

# ================= MY CODE =================
    elif data == "mycode":

        text = "📂 MY CODE\n\n"

        found = False

        for code in media_db.keys():

            if code == "views":
                continue

            text += f"• <code>{code}</code>\n"
            found = True

        if not found:
            text += "Belum ada code"

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )


    # ================= ACCOUNT =================
    elif data == "account":

        await callback_query.message.edit_text(
            f"""
🧑‍🏫 MY ACCOUNT

👤 Nama:
{callback_query.from_user.first_name}

🆔 ID:
<code>{user_id}</code>
""",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )


    # ================= HELP =================
    elif data == "help":

        await callback_query.message.edit_text(
"""
📃 HELP MENU

1. Klik Start
2. Kirim media
3. Klik Create
4. Copy code
5. Tempel code untuk download
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )


    # ================= ADMIN =================
    elif data == "admin":

        await callback_query.message.edit_text(
"""
🧑‍💼 ADMIN BOT

Developer:
@username

Bot Version:
1.0
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
    )
    # ================= UPLOAD MODE =================
    elif data == "home":

        user_uploads[user_id] = []

        msg = await callback_query.message.reply_text(
"""
📥 MODE AKTIF

Silakan kirim media/video/file

📦 Total media diterima: 0
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Create",
                        callback_data="make_code"
                    )
                ]
            ])
        )

        upload_status_message[user_id] = msg.id

    # ================= MAKE CODE =================
    elif data == "make_code":

        media_ids = user_uploads.get(user_id, [])

        if not media_ids:

            return await callback_query.message.reply_text(
                "❌ Belum ada media"
            )

        video_count = 0
        photo_count = 0
        doc_count = 0

        for msg_id in media_ids:

            try:

                msg = await client.get_messages(
                    DB_CHANNEL,
                    msg_id
                )

                if msg.video:
                    video_count += 1

                elif msg.photo:
                    photo_count += 1

                elif (
                    msg.document or
                    msg.audio or
                    msg.animation
                ):
                    doc_count += 1

            except:
                pass

        random_string = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=12
            )
        )

        code = (
            f"tzyfilebot_"
            f"{video_count}v_"
            f"{photo_count}p_"
            f"{doc_count}d_"
            f"{random_string}"
        )

# ================= CALLBACK =================
@app.on_callback_query()
async def callbacks(client, callback_query):

    await callback_query.answer()

    data = callback_query.data
    user_id = callback_query.from_user.id

    # ================= HOME / START MODE =================
    if data == "home":

        user_uploads[user_id] = []

        await callback_query.message.edit_text(
"""
📥 MODE AKTIF

Silakan kirim media/video/file

📌 Anda juga bisa tempel code

📦 Total media diterima: 0
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Create",
                        callback_data="make_code"
                    )
                ]
            ])
        )

        upload_status_message[user_id] = callback_query.message.id

    # ================= CHECK JOIN =================
    elif data == "cek_join":

        joined = await check_join(client, user_id)

        if not joined:

            return await callback_query.answer(
                "❌ Anda belum join channel",
                show_alert=True
            )

        user_uploads[user_id] = []

        await callback_query.message.edit_text(
"""
✅ Verifikasi berhasil

📥 MODE AKTIF

Silakan kirim media/video/file

📌 Anda juga bisa tempel code
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Create",
                        callback_data="make_code"
                    )
                ]
            ])
        )

        upload_status_message[user_id] = callback_query.message.id

    # ================= NEW CODE =================
    elif data == "new":

        latest = [
            x for x in media_db.keys()
            if x != "views"
        ]

        latest.reverse()

        text = "🆕 NEW CODE\n\n"

        if not latest:

            text += "Belum ada code"

        else:

            for no, code in enumerate(latest[:20], start=1):

                text += f"{no}. <code>{code}</code>\n"

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= TRENDING =================
    elif data == "trend":

        ranked = sorted(
            media_db["views"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        text = "🔥 TRENDING CODE\n\n"

        if not ranked:

            text += "Belum ada code trending"

        else:

            for no, (code, total) in enumerate(ranked[:20], start=1):

                text += (
                    f"{no}. <code>{code}</code>\n"
                    f"👁 Views: {total}\n\n"
                )

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= MY CODE =================
    elif data == "mycode":

        text = "📂 MY CODE\n\n"

        found = False

        for code in media_db.keys():

            if code == "views":
                continue

            text += f"• <code>{code}</code>\n"
            found = True

        if not found:
            text += "Belum ada code"

        await callback_query.message.edit_text(
            text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= ACCOUNT =================
    elif data == "account":

        await callback_query.message.edit_text(
f"""
🧑‍🏫 MY ACCOUNT

👤 Nama:
{callback_query.from_user.first_name}

🆔 ID:
<code>{user_id}</code>
""",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= HELP =================
    elif data == "help":

        await callback_query.message.edit_text(
"""
📃 HELP MENU

1. Klik Start
2. Kirim media
3. Klik Create
4. Copy code
5. Tempel code untuk download
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= ADMIN =================
    elif data == "admin":

        await callback_query.message.edit_text(
"""
🧑‍💼 ADMIN BOT

Developer:
@username

Bot Version:
1.0
""",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 Kembali",
                        callback_data="home"
                    )
                ]
            ])
        )

    # ================= MAKE CODE =================
    elif data == "make_code":

        media_ids = user_uploads.get(user_id, [])

        if not media_ids:

            return await callback_query.message.reply_text(
                "❌ Belum ada media"
            )

        video_count = 0
        photo_count = 0
        doc_count = 0

        for msg_id in media_ids:

            try:

                msg = await client.get_messages(
                    DB_CHANNEL,
                    msg_id
                )

                if msg.video:
                    video_count += 1

                elif msg.photo:
                    photo_count += 1

                elif (
                    msg.document or
                    msg.audio or
                    msg.animation
                ):
                    doc_count += 1

            except:
                pass

        random_string = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=12
            )
        )

        code = (
            f"tzyfilebot_"
            f"{video_count}v_"
            f"{photo_count}p_"
            f"{doc_count}d_"
            f"{random_string}"
        )

        media_db[code] = media_ids

        with open(DB_FILE, "w") as f:
            json.dump(media_db, f)

        del user_uploads[user_id]

        if user_id in upload_status_message:
            del upload_status_message[user_id]

        await callback_query.message.reply_text(
f"""
✅ Code berhasil dibuat

🔑 CODE:
<code>{code}</code>

📥 Kirim code tersebut untuk download media
""",
            parse_mode=enums.ParseMode.HTML
        )

    # ================= PAGE =================
    elif data.startswith("page|"):

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


# ================= DETECT CODE =================
@app.on_message(filters.text)
async def get_code(client, message):

    text = message.text.strip()

    found_code = None

    for saved_code in media_db.keys():

        if saved_code == "views":
            continue

        if saved_code.lower() == text.lower():

            found_code = saved_code
            break

    if not found_code:
        return

    # ================= VIEW COUNTER =================
    media_db["views"][found_code] = (
        media_db["views"].get(found_code, 0) + 1
    )

    with open(DB_FILE, "w") as f:
        json.dump(media_db, f)

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

    bot_username = (await client.get_me()).username

    media_group = []

    for index, msg_id in enumerate(current_ids):

        try:

            msg = await client.get_messages(
                DB_CHANNEL,
                msg_id
            )

            caption_text = None

            if index == len(current_ids) - 1:

                caption_text = f"""
📂 Halaman {page+1}/{total_pages}
📦 Total File: {len(media_ids)}

🤖 https://t.me/{bot_username}
"""

            if msg.photo:

                media_group.append(
                    InputMediaPhoto(
                        media=msg.photo.file_id,
                        caption=caption_text
                    )
                )

            elif msg.video:

                media_group.append(
                    InputMediaVideo(
                        media=msg.video.file_id,
                        caption=caption_text
                    )
                )

            elif msg.document:

                media_group.append(
                    InputMediaDocument(
                        media=msg.document.file_id,
                        caption=caption_text
                    )
                )

            elif msg.audio:

                media_group.append(
                    InputMediaAudio(
                        media=msg.audio.file_id,
                        caption=caption_text
                    )
                )

            elif msg.animation:

                media_group.append(
                    InputMediaAnimation(
                        media=msg.animation.file_id,
                        caption=caption_text
                    )
                )

        except Exception as e:

            print(e)

    try:

        if media_group:

            await client.send_media_group(
                chat_id=message.chat.id,
                media=media_group
            )

    except FloodWait as e:

        await asyncio.sleep(e.value + 2)

    except Exception as e:

        print(e)

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

    await message.reply_text(
        f"""
✅ Sedang menampilkan halaman {page+1}/{total_pages}

Klik tombol dibawah untuk melihat halaman berikutnya ↓
""",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= RUN =================
print("BOT RUNNING...")

app.run()

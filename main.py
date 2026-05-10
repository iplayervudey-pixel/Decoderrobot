from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import os
import random
import string
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

app = Client(
    "memory_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True
)

user_uploads = {}
media_db = {}


# ================= CHECK JOIN =================
async def check_join(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        status = str(member.status).lower()

        return any(x in status for x in [
            "member",
            "administrator",
            "owner",
            "restricted"
        ])
    except Exception as e:
        print("JOIN ERROR:", e)
        return False


# ================= COMMAND =================
@app.on_message(filters.command("setcmd"))
async def setcmd(client, message):
    await client.set_bot_commands([
        BotCommand("start", "Mulai bot"),
        BotCommand("upload", "Upload media"),
        BotCommand("download", "Download media"),
        BotCommand("help", "Bantuan"),
        BotCommand("myid", "ID saya")
    ])
    await message.reply_text("✅ Command berhasil dipasang")


# ================= MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤 Upload", callback_data="menu_upload"),
            InlineKeyboardButton("📥 Download", callback_data="menu_download")
        ],
        [
            InlineKeyboardButton("🆘 Help", callback_data="menu_help"),
            InlineKeyboardButton("🆔 My ID", callback_data="menu_myid")
        ]
    ])


# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    joined = await check_join(client, user_id)

    if not joined:
        return await message.reply_text(
            "⚠️ Join channel dulu.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
                )],
                [InlineKeyboardButton(
                    "✅ Sudah Join",
                    callback_data="cek_join"
                )]
            ])
        )

    await message.reply_text(
        "✅ Verifikasi berhasil",
        reply_markup=main_menu()
    )


# ================= HELP =================
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text(
        "Gunakan /upload untuk upload media lalu buat code."
    )


@app.on_message(filters.command("myid"))
async def myid(client, message):
    await message.reply_text(
        f"🆔 ID Kamu:\n`{message.from_user.id}`"
    )


@app.on_message(filters.command("download"))
async def download(client, message):
    await message.reply_text("📥 Kirim code media")


# ================= UPLOAD =================
@app.on_message(filters.command("upload"))
async def upload(client, message):
    user_uploads[message.from_user.id] = []

    await message.reply_text(
        "📤 Silahkan kirim media sekarang",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "➕ Tambah Media",
                callback_data="add_media"
            )],
            [InlineKeyboardButton(
                "✅ Buat Code",
                callback_data="make_code"
            )]
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
        await asyncio.sleep(1)

        copied = await message.copy(DB_CHANNEL)
        user_uploads[user_id].append(copied.id)

        total = len(user_uploads[user_id])

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "➕ Tambah Media",
                callback_data="add_media"
            )],
            [InlineKeyboardButton(
                "✅ Buat Code",
                callback_data="make_code"
            )]
        ])

        bot_msg = await message.reply_text(
            f"✅ Media berhasil disimpan\n\n📦 Total media: {total}",
            reply_markup=buttons
        )

        await asyncio.sleep(5)

        try:
            await bot_msg.delete()
            await message.delete()
        except:
            pass

    except Exception as e:
        await message.reply_text(f"❌ Error:\n{e}")


# ================= CALLBACK =================
@app.on_callback_query()
async def callbacks(client, callback_query):
    await callback_query.answer()

    data = callback_query.data
    user_id = callback_query.from_user.id

    # PAGE
    if data.startswith("page_"):
        _, code, page = data.split("_")
        page = int(page)

        if code not in media_db:
            return await callback_query.message.reply_text(
                "❌ Data tidak ditemukan"
            )

        return await send_page(
            client,
            callback_query.message,
            media_db[code],
            page,
            code
        )

    if data == "cek_join":
        joined = await check_join(client, user_id)

        if joined:
            return await callback_query.message.edit_text(
                "✅ Verifikasi berhasil",
                reply_markup=main_menu()
            )

        return await callback_query.answer(
            "❌ Kamu belum join",
            show_alert=True
        )

    elif data == "menu_upload":
        user_uploads[user_id] = []
        await callback_query.message.reply_text(
            "📤 Silahkan kirim media"
        )

    elif data == "menu_download":
        await callback_query.message.reply_text(
            "📥 Kirim code media"
        )

    elif data == "menu_help":
        await callback_query.message.reply_text(
            "Gunakan /upload lalu buat code"
        )

    elif data == "menu_myid":
        await callback_query.message.reply_text(
            f"`{user_id}`"
        )

    elif data == "add_media":
        await callback_query.answer("📤 Kirim media lagi")

    elif data == "make_code":
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

        videos = photos = docs = 0

        for msg_id in media_ids:
            msg = await client.get_messages(DB_CHANNEL, msg_id)

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
            f"✅ Code berhasil dibuat\n\n`{final_code}`"
        )


# ================= CODE DETECT =================
@app.on_message(filters.text)
async def get_code(client, message):
    code = message.text.strip()

    if code not in media_db:
        return

    media_ids = media_db[code]
    await send_page(client, message, media_ids, 0, code)


# ================= SEND PAGE =================
async def send_page(client, message, media_ids, page, code):
    per_page = 10
    start = page * per_page
    end = start + per_page
    total_pages = (len(media_ids) + per_page - 1) // per_page

    for index, msg_id in enumerate(media_ids[start:end], start=1):
        await client.copy_message(
            message.chat.id,
            DB_CHANNEL,
            msg_id,
            caption=f"📦 File {start+index}"
        )

    buttons = []
    row = []

    for i in range(total_pages):
        row.append(
            InlineKeyboardButton(
                f"{'✅' if i == page else '☑️'} {i+1}",
                callback_data=f"page_{code}_{i}"
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
                f"⬅️ Prev {page}",
                callback_data=f"page_{code}_{page-1}"
            )
        )

    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                f"Next {page+2} ➡️",
                callback_data=f"page_{code}_{page+1}"
            )
        )

    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("📤 Upload Lagi", callback_data="menu_upload"),
        InlineKeyboardButton("🆘 Menu", callback_data="menu_help")
    ])

    await message.reply_text(
        f"📄 Halaman {page+1}/{total_pages}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


app.run()

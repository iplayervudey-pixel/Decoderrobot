from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# USERNAME CHANNEL PUBLIC
# contoh: @mychannel
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

app = Client(
    "memory_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True
)


@app.on_message(filters.command("start"))
async def start(client, message):

    user_id = message.from_user.id

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

            await message.reply_text(
                "✅ Welcome To Bot"
            )

        else:

            await message.reply_text(
                "❌ Join channel dulu"
            )

    except UserNotParticipant:

        await message.reply_text(
            "❌ Kamu belum join channel"
        )

    except Exception as e:

        print(e)

        await message.reply_text(
            f"ERROR:\n{e}"
        )


@app.on_message(filters.command("id"))
async def getid(client, message):

    await message.reply_text(
        f"USER ID:\n{message.from_user.id}"
    )


app.run()

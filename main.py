from pyrogram import Client, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

app = Client(
    "bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bot Online")


@app.on_message(filters.command("id"))
async def idtest(client, message):

    try:

        chat = await client.get_chat(FORCE_CHANNEL)

        await message.reply_text(
            f"CHANNEL ID:\n{chat.id}"
        )

    except Exception as e:

        await message.reply_text(
            f"ERROR:\n{e}"
        )


app.run()

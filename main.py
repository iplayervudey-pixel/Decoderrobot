from pyrogram import Client, filters
import os

app = Client(
    "bot",
    bot_token=os.getenv("BOT_TOKEN"),
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL"))

@app.on_message(filters.command("start"))
async def start(client, message):

    try:

        member = await client.get_chat_member(
            FORCE_CHANNEL,
            message.from_user.id
        )

        await message.reply_text(
            f"STATUS: {member.status}"
        )

    except Exception as e:

        await message.reply_text(
            f"ERROR:\\n{e}"
        )

app.run()

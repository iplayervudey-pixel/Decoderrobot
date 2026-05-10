@app.on_message(filters.command("start"))
async def start(client, message):

    user_id = message.from_user.id

    try:
        member = await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        if member.status in ["member", "administrator", "owner"]:
            await message.reply_text("Welcome")
        else:
            await message.reply_text("Join channel dulu")

    except:
        await message.reply_text(
            "Silahkan join channel dulu"
        )

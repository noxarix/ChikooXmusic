import os
from pyrogram import filters, types
from chikoo import app, db

@app.on_message(filters.command(["owner"]) & app.sudoers)
async def owner_command(_, message: types.Message):
    status_msg = await message.reply_text("Gathering bot data... This may take a moment.")
    
    # Get all chats and users
    chats = await db.get_chats()
    users = await db.get_users()
    
    # Generate a file with links and IDs to prevent hitting telegram limits
    filename = "bot_database_info.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"--- {app.name} DATA ---\n\n")
            f.write(f"Total Groups: {len(chats)}\n")
            f.write(f"Total Users: {len(users)}\n\n")
            
            f.write("--- GROUPS ---\n")
            for chat_id in chats:
                # To prevent massive floodwaits, we just list IDs. 
                # If the chat has a public username, Pyrogram needs get_chat() which is slow.
                # Just listing IDs is the standard way to export without being rate limited.
                f.write(f"Group: {chat_id}\n")
                    
            f.write("\n--- USERS ---\n")
            for user_id in users:
                f.write(f"User: tg://user?id={user_id}\n")
                
        # Commands info
        commands_info = (
            "👑 <b>Owner / Hidden Commands Overview</b> 👑\n\n"
            "<b>Admin/Owner Commands (Tap to copy):</b>\n"
            "» <code>/preview</code> [text] - Interactive message builder (test before broadcast)\n"
            "» <code>/broadcast</code> [text] - Broadcast a message\n"
            "» <code>/broadcast -copy</code> [reply] - Broadcast without forward tag\n"
            "» <code>/tagall</code> [text] - Beautifully mention all members\n"
            "» <code>/cancel</code> - Stop tagging members\n"
            "» <code>/restart</code> - Restart the bot\n"
            "» <code>/ping</code> - Check bot status and latency\n\n"
            "<b>New Formatter Engine:</b>\n"
            "The standalone message formatter is fully installed in the root <code>formatter/</code> directory! "
            "It can parse custom Markdown, HTML, inline variables, and button syntaxes natively. It's built "
            "to be fully reusable for any Pyrogram bot.\n\n"
            "👉 <b>Use <code>/formatter</code> to view the full syntax guide.</b>\n\n"
            "📄 <i>Check the attached document for the list of all group and user connections.</i>"
        )
        
        await message.reply_document(
            document=filename, 
            caption=commands_info,
            quote=True
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()


@app.on_message(filters.command(["formatter", "format_guide"]) & app.sudoers)
async def formatter_guide_command(_, message: types.Message):
    guide = (
        "ʀᴇᴀᴅ ᴛʜᴇ ʙᴇʟᴏᴡ ᴛᴇxᴛ ᴄᴀʀᴇғᴜʟʟʏ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ʜᴏᴡ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴡᴏʀᴋs!\n\n"
        "sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟʟɪɴɢs:\n\n"
        "<code>{GROUPNAME}</code> - ɢʀᴏᴜᴘ's ɴᴀᴍᴇ\n"
        "<code>{NAME}</code> - ᴜsᴇʀ ɴᴀᴍᴇ\n"
        "<code>{ID}</code> - ᴜsᴇʀ ɪᴅ\n"
        "<code>{FIRSTNAME}</code> - ᴜsᴇʀ ғɪʀsᴛ ɴᴀᴍᴇ\n"
        "<code>{SURNAME}</code> - ɪғ ᴜsᴇʀ ʜᴀs sᴜʀɴᴀᴍᴇ sᴏ ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ sᴜʀɴᴀᴍᴇ ᴇʟsᴇ ɴᴏᴛʜɪɴɢ\n"
        "<code>{USERNAME}</code> - ᴜsᴇʀ ᴜsᴇʀɴᴀᴍᴇ\n\n"
        "<code>{TIME}</code> - ᴛᴏᴅᴀʏ  ᴛɪᴍᴇ\n"
        "<code>{DATE}</code> - ᴛᴏᴅᴀʏ ᴅᴀᴛᴇ\n"
        "<code>{WEEKDAY}</code> - ᴛᴏᴅᴀʏ ᴡᴇᴇᴋᴅᴀʏ\n\n"
        "NOTE: ғɪʟʟɪɴɢs ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ᴡᴇʟᴄᴏᴍᴇ ᴍᴏᴅᴜʟᴇ.\n\n"
        "sᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀᴍᴀᴛᴛɪɴɢ (Tap to copy):\n\n"
        "<code>**Bold**</code> : ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <b>Bold</b> ᴛᴇxᴛ.\n"
        "<code>~~strike~~</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <s>strike</s> ᴛᴇxᴛ.\n"
        "<code>__italic__</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <i>italic</i> ᴛᴇxᴛ\n"
        "<code>--underline--</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <u>underline</u> ᴛᴇxᴛ.\n"
        "<code>`code words`</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <code>code</code> ᴛᴇxᴛ.\n"
        "<code>||spoiler||</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <tg-spoiler>Spoiler</tg-spoiler> ᴛᴇxᴛ.\n"
        "<code>[hyperlink](google.com)</code>: ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ <a href='https://www.google.com/'>hyperlink</a> text\n"
        "<code>> hello</code>  ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs blockquote\n"
        "Note: ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ & ʜᴛᴍʟ ᴛᴀɢs.\n\n"
        "ʙᴜᴛᴛᴏɴ ғᴏʀᴍᴀᴛᴛɪɴɢ:\n\n"
        "- > text <code>~ [button text, button link]</code>\n\n"
        "ᴇxᴀᴍᴘʟᴇ:\n\n"
        "example\n"
        "button with markdown formatting <code>~ [button text, https://google.com]</code>"
    )
    
    await message.reply_text(guide, disable_web_page_preview=True)

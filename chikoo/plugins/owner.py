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
            "👑 **Owner / Hidden Commands Overview** 👑\n\n"
            "**Admin/Owner Commands:**\n"
            "» `/broadcast` [text] - Broadcast a message\n"
            "» `/broadcast -copy` [reply] - Broadcast without forward tag\n"
            "» `/tagall` [text] - Beautifully mention all members\n"
            "» `/cancel` - Stop tagging members\n"
            "» `/restart` - Restart the bot\n"
            "» `/ping` - Check bot status and latency\n\n"
            "**New Formatter Engine:**\n"
            "The standalone message formatter is fully installed in the root `formatter/` directory! "
            "It can parse custom Markdown, HTML, inline variables, and button syntaxes natively. It's built "
            "to be fully reusable for any Pyrogram bot.\n\n"
            "📄 *Check the attached document for the list of all group and user connections.*"
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

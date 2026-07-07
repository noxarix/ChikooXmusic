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
        "🛠 <b>Chikoo Formatter Syntax Guide</b>\n\n"
        "<b>1. Standard Markdown:</b>\n"
        "<code>**bold**</code> ➔ <b>bold</b>\n"
        "<code>__italic__</code> ➔ <i>italic</i>\n"
        "<code>~~strike~~</code> ➔ <s>strike</s>\n"
        "<code>||spoiler||</code> ➔ <tg-spoiler>spoiler</tg-spoiler>\n"
        "<code>--underline--</code> ➔ <u>underline</u>\n"
        "<code>[text](link)</code> ➔ <a href='https://example.com'>text</a>\n\n"
        "<b>2. Inline Variables (Tap to copy):</b>\n"
        "<code>{NAME}</code> ➔ Full Name\n"
        "<code>{FIRSTNAME}</code> ➔ First Name\n"
        "<code>{USERNAME}</code> ➔ @Username\n"
        "<code>{MENTION}</code> ➔ Clickable mention\n"
        "<code>{ID}</code> ➔ User ID\n"
        "<code>{GROUPNAME}</code> ➔ Group Title\n"
        "<code>{CHAT_ID}</code> ➔ Group ID\n"
        "<code>{MEMBER_COUNT}</code> ➔ Group member count\n"
        "<code>{TIME}</code> / <code>{DATE}</code> / <code>{WEEKDAY}</code>\n\n"
        "<b>3. Interactive Buttons (Tap to copy):</b>\n"
        "Add buttons at the bottom of your message by using <code>~</code> on a new line. Separate multiple buttons in a row with <code>|</code>.\n\n"
        "<code>~ [Click Me, https://example.com]</code>\n"
        "<code>~ [Button 1, t.me/example] | [Button 2, callback:data]</code>\n\n"
        "<b>Button Types:</b>\n"
        "• URL: <code>https://...</code> or <code>t.me/...</code>\n"
        "• Callback: <code>callback:my_data</code>\n"
        "• Switch Inline: <code>switch:query</code>\n"
        "• User Profile: <code>user:12345678</code>"
    )
    
    await message.reply_text(guide, disable_web_page_preview=True)

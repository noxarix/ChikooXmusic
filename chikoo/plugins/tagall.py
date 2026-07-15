import asyncio
from pyrogram import filters, types
from pyrogram.enums import ChatMemberStatus

from chikoo import app, lang

# Dictionary to keep track of active tagging sessions per chat
active_tags = {}

@app.on_message(filters.command(["tagall", "all"]) & filters.group & ~app.bl_users)
@lang.language()
async def tag_all(_, message: types.Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    if message.from_user:
        member = await app.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("You need to be an admin to use this command.")

    if chat_id in active_tags:
        return await message.reply_text("Tagging is already in progress... Use /cancel to stop.")
    
    active_tags[chat_id] = True
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "Hello! Wake up!"
    
    await message.reply_text("Started tagging members... (Use /cancel to stop)")
    
    try:
        async for member in app.get_chat_members(chat_id):
            if chat_id not in active_tags:
                break
                
            if member.user.is_bot or member.user.is_deleted:
                continue
                
            import html
            name = member.user.first_name if member.user.first_name else "User"
            name = name.replace("_", "").replace("*", "")
            if len(name) > 15:
                name = name[:15] + "..."
            
            # Escape HTML characters so it doesn't break the parser
            name = html.escape(name)
            
            # Use @username if available, otherwise fallback to HTML mention
            if member.user.username:
                mention = f"@{member.user.username}"
            else:
                mention = f"<a href='tg://user?id={member.user.id}'>{name}</a>"
                
            try:
                await app.send_message(chat_id, f"{text}\n\n{mention}")
            except Exception:
                pass
            
            # Sleep to prevent hitting Telegram's flood wait limit
            await asyncio.sleep(1.5)
            
    except Exception as e:
        pass
        
    if chat_id in active_tags:
        del active_tags[chat_id]
        await message.reply_text("Tagging completed.")


@app.on_message(filters.command(["cancel", "stoptag"]) & filters.group & ~app.bl_users)
@lang.language()
async def stop_tag_all(_, message: types.Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    if message.from_user:
        member = await app.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("You need to be an admin to use this command.")

    if chat_id not in active_tags:
        return await message.reply_text("No tagging process is currently active.")
        
    del active_tags[chat_id]
    await message.reply_text("Tagging process has been stopped by admin.")

from pyrogram import filters, enums
from pyrogram.types import ChatMemberUpdated

from chikoo import app, db

@app.on_chat_member_updated(filters.channel)
async def channel_added_removed(_, update: ChatMemberUpdated):
    if update.new_chat_member:
        if update.new_chat_member.user.id == app.id:
            if update.new_chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                await db.add_channel(update.chat.id)
            elif update.new_chat_member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]:
                await db.rm_channel(update.chat.id)
    elif update.old_chat_member and not update.new_chat_member:
        if update.old_chat_member.user.id == app.id:
            await db.rm_channel(update.chat.id)

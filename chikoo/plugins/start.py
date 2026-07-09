# Copyright (c) 2025 marine
# Licensed under the MIT License.
# This file is part of chikooMusic
#CHIKOO-CODER

import asyncio
from pyrogram import enums, filters, types

from chikoo import app, config, db, lang
from chikoo.helpers import buttons, utils


@app.on_message(filters.command(["help"]) & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    if m.chat.type != enums.ChatType.PRIVATE:
        return await m.reply_text(
            "Contact me in PM for help.",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("Help Menu", url=f"https://t.me/{app.me.username}?start=help")]]
            ),
        )
        
    is_sudo = m.from_user.id in app.sudoers
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang, sudoer=is_sudo),
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE
    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    key = buttons.start_key(message.lang, private)
    pic = config.RANDOM_PIC
    if str(pic).endswith((".mp4", ".gif", ".webm", ".mkv")):
        await message.reply_video(video=pic, caption=_text, reply_markup=key, quote=not private)
    else:
        await message.reply_photo(photo=pic, caption=_text, reply_markup=key, quote=not private)

    if private:
        await utils.send_log(message)
        if not await db.is_user(message.from_user.id):
            await db.add_user(message.from_user.id)
    else:
        await utils.send_log(message, True)
        if not await db.is_chat(message.chat.id):
            await db.add_chat(message.chat.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    import os
    
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    
    # Find the video in the pics folder
    video_pic = None
    try:
        welcome_video = os.path.join("pics", "9f9cb0ab87e4f7b6c061a-3544c3bdcf44adbe03.mp4")
        if os.path.exists(welcome_video):
            video_pic = welcome_video
        else:
            for f in os.listdir("pics"):
                if f.endswith((".mp4", ".gif", ".webm", ".mkv")):
                    video_pic = f"pics/{f}"
                    break
    except Exception:
        pass
        
    for member in message.new_chat_members:
        if member.id == app.id:
            await utils.send_log(message, True)
            if not await db.is_chat(message.chat.id):
                await db.add_chat(message.chat.id)
                
            bot_welcome = (
                f"🌟 <b>THANK YOU FOR ADDING ME!</b> 🌟\n\n"
                f"Thanks for adding <b>{app.name}</b> to <b>{message.chat.title}</b>, {message.from_user.mention}!\n"
                f"I'm ready to play some awesome music for you all. Enjoy! 🎶"
            )
            key = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 SUPPORT CHAT 🎵", url=config.SUPPORT_CHAT)]
            ])
            
            try:
                if video_pic:
                    await message.reply_video(video=video_pic, caption=bot_welcome, reply_markup=key)
                else:
                    pic = config.RANDOM_PIC
                    if str(pic).endswith((".mp4", ".gif", ".webm", ".mkv")):
                        await message.reply_video(video=pic, caption=bot_welcome, reply_markup=key)
                    else:
                        await message.reply_photo(photo=pic, caption=bot_welcome, reply_markup=key)
            except Exception:
                pass
        else:
            # Send welcome message for regular users
            text = (
                f"🌟 <b>WELCOME</b> {member.mention}!\n\n"
                f"📋 <b>GROUP:</b> {message.chat.title}\n"
                f"🆔 <b>YOUR ID:</b> <code>{member.id}</code>\n"
                f"👤 <b>USERNAME:</b> {f'@{member.username}' if member.username else 'None'}\n\n"
                f"<b><u>HOPE YOU FIND GOOD VIBES, NEW FRIENDS, AND LOTS OF FUN HERE!</u></b> 🌟"
            )
            key = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 ADD ME IN YOUR GROUP 🎵", url=f"https://t.me/{app.username}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")]
            ])
            
            try:
                if video_pic:
                    await message.reply_video(video=video_pic, caption=text, reply_markup=key)
                else:
                    # Fallback to random pic if no video is found
                    pic = config.RANDOM_PIC
                    if str(pic).endswith((".mp4", ".gif", ".webm", ".mkv")):
                        await message.reply_video(video=pic, caption=text, reply_markup=key)
                    else:
                        await message.reply_photo(photo=pic, caption=text, reply_markup=key)
            except Exception:
                pass

@app.on_message(filters.left_chat_member, group=8)
@lang.language()
async def _left_member(_, message: types.Message):
    if message.left_chat_member.id == app.id:
        try:
            if not await db.is_logger():
                return
            
            chat_obj = message.chat
            invite_link = f"https://t.me/{chat_obj.username}" if chat_obj.username else "Private (No Link)"
            
            text = (
                f"<b>{app.name} Removed From A Group</b>\n\n"
                f"<b>Chat Name:</b> {chat_obj.title}\n"
                f"<b>Chat ID:</b> <code>{chat_obj.id}</code>\n"
                f"<b>Chat Link:</b> {invite_link}\n"
                f"<b>Removed By:</b> {message.from_user.mention}"
            )
            await app.send_message(app.logger, text)
        except Exception:
            pass

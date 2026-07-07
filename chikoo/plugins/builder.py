import uuid
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from chikoo import app, db
from formatter import parse

# We store previews in memory. 
# Key: Unique ID (string)
# Value: dict with {"text": raw_text, "user_id": creator_user_id}
PREVIEWS = {}

@app.on_message(filters.command(["preview", "make_msg"]) & app.sudoers)
async def preview_message(_, message: types.Message):
    # Extract raw text
    raw_text = None
    if message.reply_to_message:
        raw_text = message.reply_to_message.text or message.reply_to_message.caption
        # If user typed something along with the command (like buttons), append or use it
        if len(message.command) > 1:
            cmd_text = message.text.split(None, 1)[1]
            if raw_text:
                raw_text += f"\n{cmd_text}"
            else:
                raw_text = cmd_text
    else:
        if len(message.command) > 1:
            raw_text = message.text.split(None, 1)[1]
            
    if not raw_text and not message.reply_to_message:
        return await message.reply_text("Please provide text to preview or reply to a message containing the text or media.")

    # Generate a unique ID for this preview session
    preview_id = str(uuid.uuid4())[:8]
    PREVIEWS[preview_id] = {
        "text": raw_text,
        "user_id": message.from_user.id
    }

    # Parse it to see exactly how it will look
    parsed = await parse(raw_text, user=message.from_user, chat=message.chat)
    
    # We will merge the buttons from the parsed text with our control panel
    kb = []
    
    # Check if the parsed output has buttons
    if parsed.reply_markup and "inline_keyboard" in parsed.reply_markup:
        # Extract the buttons created by the formatter
        # Since it's a raw dict from our formatter, we construct standard Pyrogram buttons
        for row in parsed.reply_markup["inline_keyboard"]:
            new_row = []
            for btn in row:
                if "url" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
                elif "callback_data" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
                elif "user_id" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], user_id=btn["user_id"]))
                elif "switch_inline_query" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], switch_inline_query=btn["switch_inline_query"]))
            kb.append(new_row)

    # Append our control panel at the very bottom
    kb.append([
        InlineKeyboardButton("📡 Broadcast to Groups", callback_data=f"bc_grp_{preview_id}"),
        InlineKeyboardButton("👥 Broadcast to Users", callback_data=f"bc_usr_{preview_id}")
    ])
    kb.append([
        InlineKeyboardButton("❌ Cancel Preview", callback_data=f"bc_cancel_{preview_id}")
    ])

    reply_markup = InlineKeyboardMarkup(kb)

    try:
        if message.reply_to_message and not (message.reply_to_message.text and len(message.command) == 1):
            kwargs = {}
            if reply_markup:
                kwargs["reply_markup"] = reply_markup
            if parsed and parsed.text and not message.reply_to_message.sticker:
                kwargs["caption"] = parsed.text
                
            await message.reply_to_message.copy(
                message.chat.id,
                **kwargs
            )
        else:
            await message.reply_text(
                text=parsed.text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        await message.reply_text(f"❌ Error rendering preview:\n`{e}`")


@app.on_callback_query(filters.regex(r"^bc_(grp|usr|cancel)_(.+)$"))
async def preview_callbacks(client, callback_query: types.CallbackQuery):
    action = callback_query.matches[0].group(1)
    preview_id = callback_query.matches[0].group(2)

    # Validate preview exists
    if preview_id not in PREVIEWS:
        return await callback_query.answer("This preview session has expired or is invalid.", show_alert=True)

    session = PREVIEWS[preview_id]
    
    # Only allow the creator to use the control panel
    if callback_query.from_user.id != session["user_id"]:
        return await callback_query.answer("You did not create this preview.", show_alert=True)

    if action == "cancel":
        del PREVIEWS[preview_id]
        return await callback_query.message.delete()

    raw_text = session["text"]
    
    # We don't want to block the callback query loop, so we'll answer it immediately
    await callback_query.answer("Starting broadcast...", show_alert=True)
    
    # Delete the preview message so the buttons can't be clicked twice
    await callback_query.message.delete()
    
    # Send a status message
    status_msg = await callback_query.message.reply_text("Broadcast started via Interactive Builder...")
    
    # Parse the text globally once for the broadcast
    parsed = await parse(raw_text)
    
    # Import the broadcast_to_targets function dynamically to avoid circular imports
    from chikoo.plugins.broadcast import broadcast_to_targets
    
    if action == "grp":
        chat_ids = await db.get_chats()
        sent, pinned = await broadcast_to_targets(
            client, chat_ids, query=raw_text, parsed=parsed
        )
        try:
            await status_msg.edit_text(f"✅ Successfully Broadcasted to {sent} groups.")
        except:
            pass

    elif action == "usr":
        user_ids = await db.get_users()
        sent, pinned = await broadcast_to_targets(
            client, user_ids, query=raw_text, parsed=parsed
        )
        try:
            await status_msg.edit_text(f"✅ Successfully Broadcasted to {sent} users.")
        except:
            pass

    # Cleanup memory
    if preview_id in PREVIEWS:
        del PREVIEWS[preview_id]

@app.on_message(filters.private & filters.text & app.sudoers & ~filters.regex(r"^/"))
async def live_formatter_preview(_, message: types.Message):
    """
    Interactive Formatter Sandbox.
    If a sudoer sends plain text to the bot's PM, it is automatically parsed 
    and echoed back as a live preview.
    """
    raw_text = message.text
    
    parsed = await parse(raw_text, user=message.from_user, chat=message.chat)
    
    kb = []
    if parsed.reply_markup and "inline_keyboard" in parsed.reply_markup:
        for row in parsed.reply_markup["inline_keyboard"]:
            new_row = []
            for btn in row:
                if "url" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
                elif "callback_data" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
                elif "user_id" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], user_id=btn["user_id"]))
                elif "switch_inline_query" in btn:
                    new_row.append(InlineKeyboardButton(text=btn["text"], switch_inline_query=btn["switch_inline_query"]))
            kb.append(new_row)
            
    reply_markup = InlineKeyboardMarkup(kb) if kb else None
    
    try:
        await message.reply_text(
            text=parsed.text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"❌ Error rendering preview:\n<code>{e}</code>")

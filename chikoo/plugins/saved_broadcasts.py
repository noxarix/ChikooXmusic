import re
import uuid
import time
import asyncio
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from chikoo import app, db
from formatter import parse
from chikoo.plugins.builder import PREVIEWS
from chikoo.plugins.broadcast import broadcast_to_targets

@app.on_message(filters.command(["save_broadcast"]) & app.sudoers)
async def save_broadcast(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/save_broadcast <name>` (reply to your formatted text)")
    
    name = message.command[1].lower()
    
    raw_text = None
    if message.reply_to_message:
        raw_text = message.reply_to_message.text or message.reply_to_message.caption
        
    if not raw_text:
        return await message.reply_text("Please reply to the formatted text you want to save.")
        
    existing = await db.saved_broadcasts.find_one({"name": name})
    
    await db.saved_broadcasts.update_one(
        {"name": name},
        {"$set": {"text": raw_text}},
        upsert=True
    )
    
    if existing:
        await message.reply_text(f"✅ Successfully updated saved broadcast: `{name}`")
    else:
        await message.reply_text(f"✅ Successfully saved new broadcast: `{name}`")


@app.on_message(filters.command(["saved_broadcasts"]) & app.sudoers)
async def list_saved_broadcasts(_, message: types.Message):
    cursor = db.saved_broadcasts.find({})
    saved = await cursor.to_list(length=100)
    
    if not saved:
        return await message.reply_text("You don't have any saved broadcasts yet.")
        
    text = "📁 **Saved Broadcasts:**\n\n"
    for item in saved:
        text += f"» `{item['name']}`\n"
        
    text += "\nTo load and preview one, use: `/load_broadcast <name>`\n"
    text += "To delete one, use: `/del_broadcast <name>`"
    await message.reply_text(text)


@app.on_message(filters.command(["del_broadcast"]) & app.sudoers)
async def del_broadcast(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/del_broadcast <name>`")
        
    name = message.command[1].lower()
    result = await db.saved_broadcasts.delete_one({"name": name})
    
    if result.deleted_count > 0:
        await message.reply_text(f"🗑 Deleted saved broadcast: `{name}`")
    else:
        await message.reply_text(f"❌ Could not find saved broadcast: `{name}`")


@app.on_message(filters.command(["load_broadcast"]) & app.sudoers)
async def load_broadcast(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/load_broadcast <name>`")
        
    name = message.command[1].lower()
    
    saved = await db.saved_broadcasts.find_one({"name": name})
    if not saved:
        return await message.reply_text(f"❌ Could not find saved broadcast: `{name}`")
        
    raw_text = saved["text"]
    
    preview_id = str(uuid.uuid4())[:8]
    PREVIEWS[preview_id] = {
        "text": raw_text,
        "user_id": message.from_user.id
    }

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

    kb.append([
        InlineKeyboardButton("📡 Broadcast to Groups", callback_data=f"bc_grp_{preview_id}"),
        InlineKeyboardButton("👥 Broadcast to Users", callback_data=f"bc_usr_{preview_id}")
    ])
    kb.append([
        InlineKeyboardButton("❌ Cancel Preview", callback_data=f"bc_cancel_{preview_id}")
    ])

    reply_markup = InlineKeyboardMarkup(kb)

    try:
        await message.reply_text(
            text=f"**[Loaded: {name}]**\n\n" + parsed.text,
            entities=parsed.entities,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"❌ Error rendering preview:\n`{e}`")


@app.on_message(filters.command(["schedule_broadcast"]) & app.sudoers)
async def schedule_broadcast(_, message: types.Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: `/schedule_broadcast <groups|users> <time_delay>`\nExample: `/schedule_broadcast groups 2h` or `/schedule_broadcast users 30m`\n\nReply to the text to broadcast, or pass a saved broadcast name as the 3rd argument (e.g. `/schedule_broadcast groups 1h promo_1`)")
        
    target = message.command[1].lower()
    if target not in ["groups", "users"]:
        return await message.reply_text("Target must be `groups` or `users`.")
        
    delay_str = message.command[2].lower()
    
    match = re.match(r"^(\d+)([smh])$", delay_str)
    if not match:
        return await message.reply_text("Invalid time format! Use `s` for seconds, `m` for minutes, `h` for hours (e.g. `10s`, `5m`, `2h`).")
        
    amount = int(match.group(1))
    unit = match.group(2)
    
    if unit == 's':
        delay_seconds = amount
    elif unit == 'm':
        delay_seconds = amount * 60
    elif unit == 'h':
        delay_seconds = amount * 3600
        
    execute_time = time.time() + delay_seconds
    
    raw_text = None
    saved_name = None
    
    if len(message.command) > 3:
        saved_name = message.command[3].lower()
        saved = await db.saved_broadcasts.find_one({"name": saved_name})
        if not saved:
            return await message.reply_text(f"❌ Could not find saved broadcast: `{saved_name}`")
        raw_text = saved["text"]
    elif message.reply_to_message:
        raw_text = message.reply_to_message.text or message.reply_to_message.caption
        
    if not raw_text:
        return await message.reply_text("Please reply to the text to schedule, or specify a saved broadcast name!")
        
    task_id = str(uuid.uuid4())[:8]
    
    await db.scheduled_broadcasts.insert_one({
        "task_id": task_id,
        "target": target,
        "execute_time": execute_time,
        "text": raw_text,
        "scheduled_by": message.from_user.id
    })
    
    await message.reply_text(f"✅ Successfully scheduled a broadcast to {target} in **{delay_str}**!\nTask ID: `{task_id}`")


async def scheduler_loop(client):
    while True:
        try:
            now = time.time()
            cursor = db.scheduled_broadcasts.find({"execute_time": {"$lte": now}})
            tasks = await cursor.to_list(length=50)
            
            for task in tasks:
                raw_text = task["text"]
                target = task["target"]
                
                parsed = await parse(raw_text)
                
                if target == "groups":
                    targets = await db.get_chats()
                else:
                    targets = await db.get_users()
                    
                await broadcast_to_targets(client, targets, query=raw_text, parsed=parsed)
                
                # Delete the task after executing
                await db.scheduled_broadcasts.delete_one({"_id": task["_id"]})
                
                # Notify the person who scheduled it
                try:
                    await client.send_message(
                        task["scheduled_by"],
                        f"✅ Scheduled broadcast completed successfully!"
                    )
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in scheduler_loop: {e}")
            
        await asyncio.sleep(10)

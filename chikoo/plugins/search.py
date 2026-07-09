import aiohttp
from pyrogram import filters, types
from chikoo import app, lang
from chikoo.helpers import utils

search_cache = {}

@app.on_message(filters.command(["search"]))
@lang.language()
async def search_command(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a query to search. Example: `/search shape of you`")
    
    query = " ".join(message.command[1:])
    sent = await message.reply_text("🔍 Searching for music...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.airbeats.xyz/api/search/songs",
                params={"query": query, "limit": 8}
            ) as response:
                if response.status != 200:
                    return await sent.edit_text("❌ Failed to fetch results from the API.")
                
                data = await response.json()
                
        if not data.get("success") or not data.get("data") or not data["data"].get("results"):
            return await sent.edit_text("❌ No results found.")
            
        results = data["data"]["results"]
        user_id = message.from_user.id
        search_cache[user_id] = results
        
        buttons = []
        text = f"/search {query}"
        for idx, song in enumerate(results):
            name = song.get("name", "Unknown")
            artists = "Unknown"
            if "artists" in song and "primary" in song["artists"] and song["artists"]["primary"]:
                artists = " & ".join([a.get("name", "") for a in song["artists"]["primary"]])
            
            if idx == 0 and song.get("duration"):
                m, s = divmod(int(song["duration"]), 60)
                button_text = f"• {m}:{s:02d} • {name} — {artists}"
            else:
                button_text = f"{name} — {artists}"
                
            if len(button_text) > 60:
                button_text = button_text[:57] + "..."
            buttons.append([types.InlineKeyboardButton(button_text, callback_data=f"srch_dl_{idx}_{user_id}")])
            
        buttons.append([types.InlineKeyboardButton("➕ More tracks", callback_data="help close")])
        buttons.append([
            types.InlineKeyboardButton("🔍", switch_inline_query_current_chat=""),
            types.InlineKeyboardButton("↗️", switch_inline_query="")
        ])
        buttons.append([types.InlineKeyboardButton("➕ Add to group", url=f"https://t.me/{app.me.username}?startgroup=true")])
        
        await sent.edit_text(
            text=text,
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await sent.edit_text(f"❌ An error occurred: {str(e)}")

@app.on_callback_query(filters.regex(r"^srch_dl_"))
async def search_download_cb(_, query: types.CallbackQuery):
    data = query.data.split("_")
    idx = int(data[2])
    user_id = int(data[3])
    
    if query.from_user.id != user_id:
        return await query.answer("This search result is not for you!", show_alert=True)
        
    if user_id not in search_cache or len(search_cache[user_id]) <= idx:
        return await query.answer("Search session expired. Please search again.", show_alert=True)
        
    song = search_cache[user_id][idx]
    download_urls = song.get("downloadUrl", [])
    
    if not download_urls:
        return await query.answer("No download URL found for this song.", show_alert=True)
        
    # Get highest quality (320kbps usually last)
    best_url = download_urls[-1].get("url")
    name = song.get("name", "Audio")
    artists = "Unknown"
    if "artists" in song and "primary" in song["artists"] and song["artists"]["primary"]:
        artists = " & ".join([a.get("name", "") for a in song["artists"]["primary"]])
    
    await query.answer("Downloading and sending audio... Please wait.")
    
    file_name = f"{name} - {artists}.m4a".replace("/", "_").replace("\\", "_").replace(":", "_")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(best_url) as resp:
                if resp.status == 200:
                    with open(file_name, "wb") as f:
                        f.write(await resp.read())
                else:
                    return await query.message.reply_text("❌ Failed to download audio.")
                    
        await query.message.reply_audio(
            audio=file_name,
            title=name,
            performer=artists,
            caption=f"@{app.me.username} | info",
            quote=False
        )
        import os
        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as e:
        await query.message.reply_text(f"❌ Failed to send audio: {str(e)}")

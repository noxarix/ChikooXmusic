import random
from pyrogram import enums, filters, types

from chikoo import app
from chikoo.helpers._inline import Inline
from chikoo.plugins.play import play_hndlr

inline = Inline()

# Song databases based on moods provided
MOOD_SONGS = {
    "sad": [
        "Ashe – Moral of the Story", "Billie Eilish – everything i wanted",
        "Lewis Capaldi – Someone You Loved", "Dean Lewis – Be Alright",
        "Olivia Rodrigo – traitor", "Alec Benjamin – Let Me Down Slowly",
        "Tom Odell – Another Love", "Benson Boone – In The Stars",
        "Labrinth – Jealous", "James Arthur – Empty Space",
        "Christina Perri – A Thousand Years", "Lord Huron – The Night We Met",
        "Lady Gaga & Bruno Mars – Die With A Smile", "Billie Eilish – What Was I Made For?",
        "Rosa Linn – SNAP"
    ],
    "motivational": [
        "Imagine Dragons – Believer", "Imagine Dragons – Warriors",
        "Imagine Dragons – Whatever It Takes", "The Score – Unstoppable",
        "The Score – Legend", "NEFFEX – Fight Back",
        "NEFFEX – Grateful", "Alan Walker – Hero",
        "Fall Out Boy – Centuries", "Sia – Unstoppable",
        "Katy Perry – Roar", "Survivor – Eye of the Tiger"
    ],
    "party": [
        "Dua Lipa – Houdini", "Dua Lipa – Dance The Night",
        "David Guetta & Bebe Rexha – I'm Good", "The Weeknd – Blinding Lights",
        "OneRepublic – I Ain't Worried", "Ava Max – Kings & Queens",
        "Doja Cat – Paint The Town Red", "Black Eyed Peas – Pump It",
        "Bruno Mars – 24K Magic", "Justin Timberlake – Can't Stop The Feeling"
    ],
    "chill": [
        "d4vd – Here With Me", "d4vd – Romantic Homicide",
        "Cigarettes After Sex – Apocalypse", "Cigarettes After Sex – Nothing's Gonna Hurt You Baby",
        "Joji – Glimpse of Us", "Keshi – Limbo",
        "Stephen Sanchez – Until I Found You", "Ruth B. – Dandelions",
        "Conan Gray – Heather", "Laufey – From The Start"
    ],
    "romantic": [
        "Stephen Sanchez – Until I Found You", "Ed Sheeran – Perfect",
        "James Arthur – Say You Won't Let Go", "Bruno Mars – Just The Way You Are",
        "Christina Perri – A Thousand Years", "Lady Gaga & Bradley Cooper – Shallow",
        "One Direction – Night Changes", "Taylor Swift – Lover",
        "Elvis Presley – Can't Help Falling in Love", "Daniel Caesar – Best Part"
    ],
    "dark": [
        "Billie Eilish – bury a friend", "Halsey – Control",
        "Imagine Dragons – Natural", "Grandson – Blood // Water",
        "AViVA – GRRRLS", "Besomorph – After Dark",
        "Kordhell – Murder In My Mind", "Unlike Pluto – Everything Black",
        "Tommee Profitt – In The End", "Hidden Citizens – Paint It Black"
    ],
    "hindi_emotional": [
        "Anuv Jain – Husn", "Anuv Jain – Baarishein", "Anuv Jain – Gul", "Anuv Jain – Alag Aasmaan",
        "Prateek Kuhad – Kasoor", "Prateek Kuhad – Cold/Mess", "OAFF & Savera – Doobey",
        "Taba Chake – Walk With Me", "Taba Chake – Aao Chalein", "Arijit Singh – Shayad",
        "Arijit Singh – Phir Le Aaya Dil", "Arijit Singh – Channa Mereya", "Arijit Singh – Agar Tum Saath Ho",
        "Arijit Singh – Satranga", "Bairan", "Inaam"
    ],
    "hindi_love": [
        "Heeriye", "Chaleya", "Apna Bana Le", "Ranjha", "Kesariya",
        "O Maahi", "Kaise Hua", "Tera Ban Jaunga", "Raataan Lambiyan",
        "Tere Hawaale", "Tum Se Hi", "Tera Hone Laga Hoon"
    ],
    "hindi_party": [
        "Tauba Tauba", "Kala Chashma", "Naach Meri Rani", "Bijlee Bijlee",
        "Jugnu", "Gallan Goodiyaan", "Ghungroo", "Nashe Si Chadh Gayi",
        "Bom Diggy", "Kar Gayi Chull", "Illegal Weapon 2.0", "What Jhumka?"
    ],
    "hindi_indie": [
        "Husn", "Bairan", "Gul", "Baarishein", "Alag Aasmaan",
        "Kasoor", "Riha", "Choo Lo", "Kho Gaye Hum Kahan",
        "Iktara", "Aaftab", "Aise Kyun"
    ],
    "taste_match": [
        "Tom Odell – Another Love", "Benson Boone – Beautiful Things",
        "Billie Eilish – everything i wanted", "d4vd – Here With Me",
        "Lord Huron – The Night We Met", "Stephen Sanchez – Until I Found You",
        "Anuv Jain – Gul", "Prateek Kuhad – Kasoor", "Taba Chake – Walk With Me",
        "Arijit Singh – O Maahi", "Imagine Dragons – Demons", "The Score – Legend",
        "Sia – Unstoppable", "OneRepublic – I Lived", "Lady Gaga & Bruno Mars – Die With A Smile"
    ]
}

# Create a flattened list for 'random'
ALL_SONGS = [song for category in MOOD_SONGS.values() for song in category]

@app.on_callback_query(filters.regex("^mood_menu$"))
async def mood_menu_cb(_, callback_query: types.CallbackQuery):
    await callback_query.answer()
    
    # Check if this was pressed in the player controls or start menu
    text = (
        "🎭 **Auto Play Moods**\n\n"
        "Select a vibe below, and I will automatically pick and play a random song from that category!"
    )
    
    try:
        await callback_query.message.reply_text(
            text=text,
            reply_markup=inline.mood_markup()
        )
    except Exception:
        pass


@app.on_callback_query(filters.regex(r"^play_mood (.*)$"))
async def play_mood_cb(client, callback_query: types.CallbackQuery):
    mood = callback_query.matches[0].group(1)
    
    # You can't play in PM unless you are connected to a call (which is not possible in PM)
    if callback_query.message.chat.type == enums.ChatType.PRIVATE:
        return await callback_query.answer("❌ You must use this feature inside a Group Chat!", show_alert=True)

    await callback_query.answer("🎵 Selecting a song for you...", show_alert=True)
    
    # Select random song
    if mood == "random":
        song = random.choice(ALL_SONGS)
    else:
        song = random.choice(MOOD_SONGS.get(mood, ALL_SONGS))
        
    # Delete the mood menu if it's standalone, or just leave it if it's the player
    try:
        await callback_query.message.delete()
    except Exception:
        pass

    # We mock a message object to pass into `play_hndlr`
    mock_message = types.Message(
        id=callback_query.message.id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date,
        text=f"/play {song}",
        command=["play"] + song.split(" ")
    )
    
    # Attach lang dictionary since play_hndlr relies on it
    # We can fetch the chat language
    from chikoo import db, lang
    _language = await db.get_lang(callback_query.message.chat.id)
    setattr(mock_message, "lang", lang.languages.get(_language, lang.languages["en"]))

    # Call the play handler programmatically
    await play_hndlr(client, mock_message, url=song)

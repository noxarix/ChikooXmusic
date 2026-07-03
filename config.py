# CHIKOO-CODER
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", "17596251"))
        self.API_HASH = getenv("API_HASH", "e58343b4c0193e293e391daf97603fcd")

        self.BOT_TOKEN = getenv("BOT_TOKEN", "Apna Bot Token")
        self.MONGO_URL = getenv("MONGO_URL", "Apna Mongo Db Dalo")

        self.LOGGER_ID = int(getenv("LOGGER_ID", "-1003854544060"))
        self.OWNER_ID = int(getenv("OWNER_ID", "8455806295"))
        
        self.SESSION1 = getenv("SESSION", "Apna String Dalo")
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/BrokenXworld")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/Music_Brigade_Chatting_zone")

        self.AUTO_END: bool = getenv("AUTO_END", False)
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", False)
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", True)

        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "50"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", "5400"))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "20"))
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/1f070ea3147e2a3ef44e4.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/6notyf.jpg")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/6notyf.jpg")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    @property
    def STATS_IMG(self):
        return "pics/ChikooMusic.png"

    @property
    def RANDOM_PIC(self):
        import os, random
        try:
            pics = [
                f"pics/{x}" for x in os.listdir("pics") 
                if x.endswith((".jpg", ".png", ".jpeg", ".mp4", ".gif", ".webm", ".mkv"))
                and x.lower() != "chikoomusic.png"
            ]
            return random.choice(pics) if pics else self.START_IMG
        except Exception:
            return self.START_IMG

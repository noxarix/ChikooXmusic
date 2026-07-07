
from pyrogram import enums, types
from pyrogram.enums import ButtonStyle

from chikoo import app, config, lang
from chikoo.core.lang import lang_codes


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
        _lang: dict = None,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}", style=ButtonStyle.PRIMARY)]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}", style=ButtonStyle.SUCCESS),
                    self.ikb(text="II", callback_data=f"controls pause {chat_id}", style=ButtonStyle.SUCCESS),
                    self.ikb(text="⥁", callback_data=f"controls replay {chat_id}", style=ButtonStyle.PRIMARY),
                    self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}", style=ButtonStyle.DANGER),
                    self.ikb(text="▢", callback_data=f"controls stop {chat_id}", style=ButtonStyle.DANGER),
                ]
            )
            if not _lang:
                _lang = lang.languages["en"]
            keyboard.append(
                [
                    self.ikb(
                        text=_lang.get("add_me", "✙ 𝐀ᴅᴅ 𝐌є 𝐈η 𝐘συʀ 𝐆ʀσυᴘ ✙"),
                        url=f"https://t.me/{app.username}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users",
                        style=ButtonStyle.PRIMARY,
                    ),
                ]
            )
            keyboard.append(
                [
                    self.ikb(
                        text=_lang.get("auto_play", "🎭 𝐀𝐮𝐭𝐨 𝐏𝐥𝐚𝐲 𝐌𝐨𝐨𝐝𝐬"),
                        callback_data="mood_menu",
                        style=ButtonStyle.SUCCESS,
                    ),
                    self.ikb(
                        text=_lang.get("close", "⌯ 𝐂ʟσsє ⌯"),
                        callback_data="help close",
                        style=ButtonStyle.DANGER,
                    ),
                ]
            )
        return self.ikm(keyboard)


    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [
                    self.ikb(text=_lang["back"], callback_data="help back", style=ButtonStyle.PRIMARY),
                    self.ikb(text=_lang["close"], callback_data="help close", style=ButtonStyle.DANGER),
                ]
            ]
        else:
            cbs = ["admins", "auth", "blist", "lang", "ping", "play", "queue", "stats", "sudo"]
            buttons = [
                self.ikb(text=_lang[f"help_{i}"], callback_data=f"help {cb}", style=ButtonStyle.PRIMARY)
                for i, cb in enumerate(cbs)
            ]
            rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
            rows.append(
                [
                    self.ikb(text=_lang["back"], callback_data="help_back_start", style=ButtonStyle.PRIMARY),
                    self.ikb(text=_lang["close"], callback_data="help close", style=ButtonStyle.DANGER),
                ]
            )

        return self.ikm(rows)

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        langs = lang.get_languages()

        buttons = [
            self.ikb(
                text=f"{name} ({code}) {'✔️' if code == _lang else ''}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=f"controls force {chat_id} {item_id}",
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=f"controls {_action} {chat_id} q",
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            ]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=lang["play_mode"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=admin_only, callback_data="settings play"),
                ],
                [
                    self.ikb(
                        text=lang["cmd_delete"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=cmd_delete, callback_data="settings delete"),
                ],
                [
                    self.ikb(
                        text=lang["language"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=lang_codes[language], callback_data="language"),
                ],
            ]
        )

    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
                    text=lang["add_me"],
                    url=f"https://t.me/{app.username}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users", style=ButtonStyle.PRIMARY
                )
            ],
            [
                self.ikb(text=lang["help"], callback_data="help", style=ButtonStyle.PRIMARY),
                self.ikb(text="🎭 Auto Play Moods", callback_data="mood_menu", style=ButtonStyle.PRIMARY)
            ],
            [
                self.ikb(text=lang["support"], url=config.SUPPORT_CHAT, style=ButtonStyle.SUCCESS),
                self.ikb(text=lang["channel"], url=config.SUPPORT_CHANNEL, style=ButtonStyle.SUCCESS),
            ],
        ]
        if private:
            rows += [
                [
                    self.ikb(text=lang["chikooowner"], user_id=config.OWNER_ID, style=ButtonStyle.DANGER),
                    self.ikb(
                        text=lang["source"],
                        url="https://github.com/noxarix/ChikooXmusic", style=ButtonStyle.DANGER
                    )
                ]
            ]
        else:
            rows += [[self.ikb(text=lang["language"], callback_data="language")]]
        return self.ikm(rows)

    def mood_markup(self) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(text="💔 Sad", callback_data="play_mood sad", style=ButtonStyle.PRIMARY),
                    self.ikb(text="🔥 Motivational", callback_data="play_mood motivational", style=ButtonStyle.PRIMARY)
                ],
                [
                    self.ikb(text="🎉 Party", callback_data="play_mood party", style=ButtonStyle.SUCCESS),
                    self.ikb(text="🌙 Chill", callback_data="play_mood chill", style=ButtonStyle.SUCCESS)
                ],
                [
                    self.ikb(text="❤️ Romantic", callback_data="play_mood romantic", style=ButtonStyle.PRIMARY),
                    self.ikb(text="😈 Dark", callback_data="play_mood dark", style=ButtonStyle.PRIMARY)
                ],
                [
                    self.ikb(text="🎧 Hindi Emo", callback_data="play_mood hindi_emotional", style=ButtonStyle.SUCCESS),
                    self.ikb(text="💖 Hindi Love", callback_data="play_mood hindi_love", style=ButtonStyle.SUCCESS)
                ],
                [
                    self.ikb(text="🎉 Hindi Party", callback_data="play_mood hindi_party", style=ButtonStyle.PRIMARY),
                    self.ikb(text="🌌 Indie/Lo-fi", callback_data="play_mood hindi_indie", style=ButtonStyle.PRIMARY)
                ],
                [
                    self.ikb(text="🎵 Taste Match", callback_data="play_mood taste_match", style=ButtonStyle.SUCCESS),
                    self.ikb(text="🎲 Surprise Me", callback_data="play_mood random", style=ButtonStyle.SUCCESS)
                ],
                [
                    self.ikb(text="⬅️ Back", callback_data="help_back_start", style=ButtonStyle.DANGER),
                    self.ikb(text="❌ Close", callback_data="help close", style=ButtonStyle.DANGER)
                ]
            ]
        )

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(text="❐", copy_text=link),
                    self.ikb(text="Youtube", url=link),
                ],
            ]
        )

import datetime
import re
from typing import Callable, Dict, Any, Optional
from pyrogram.types import User, Chat

class VariableParser:
    def __init__(self):
        self.custom_variables: Dict[str, Callable[..., str]] = {}

    def register_variable(self, name: str, func: Callable[..., str]):
        """
        Register a custom variable.
        func should take kwargs (user, chat, bot) and return a string.
        """
        self.custom_variables[name.upper()] = func

    def parse(self, text: str, user: Optional[User] = None, chat: Optional[Chat] = None, bot: Optional[User] = None) -> str:
        if not text:
            return text

        now = datetime.datetime.now()
        
        # Default user variables
        first_name = user.first_name if user and user.first_name else ""
        last_name = user.last_name if user and user.last_name else ""
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else ""
        username = f"@{user.username}" if user and user.username else ""
        user_id = str(user.id) if user else ""
        mention = user.mention if user else full_name

        # Default chat variables
        chat_title = chat.title if chat and chat.title else ""
        chat_id = str(chat.id) if chat else ""
        member_count = str(chat.members_count) if chat and getattr(chat, 'members_count', None) else ""

        # Default bot variables
        bot_name = bot.first_name if bot else ""
        bot_username = f"@{bot.username}" if bot and bot.username else ""

        replacements = {
            "{NAME}": full_name,
            "{FIRSTNAME}": first_name,
            "{SURNAME}": last_name,
            "{LASTNAME}": last_name,
            "{USERNAME}": username,
            "{MENTION}": mention,
            "{ID}": user_id,

            "{GROUPNAME}": chat_title,
            "{CHAT_ID}": chat_id,
            "{MEMBER_COUNT}": member_count,

            "{BOT_NAME}": bot_name,
            "{BOT_USERNAME}": bot_username,

            "{DATE}": now.strftime("%Y-%m-%d"),
            "{TIME}": now.strftime("%H:%M:%S"),
            "{WEEKDAY}": now.strftime("%A"),
            "{YEAR}": now.strftime("%Y"),
            "{MONTH}": now.strftime("%B"),
        }

        # Apply default replacements
        for key, value in replacements.items():
            if value: # Only replace if value exists, or maybe replace empty string?
                # Usually we replace even if empty to remove the placeholder
                text = text.replace(key, str(value))
            else:
                text = text.replace(key, "")

        # Apply custom replacements
        for key, func in self.custom_variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                try:
                    val = func(user=user, chat=chat, bot=bot)
                    text = text.replace(placeholder, str(val) if val else "")
                except Exception:
                    pass

        return text

# Global instance for easy importing
variable_parser = VariableParser()

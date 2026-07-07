from dataclasses import dataclass
from typing import List, Optional
from pyrogram.types import MessageEntity, InlineKeyboardMarkup

@dataclass
class ParsedMessage:
    text: str
    entities: Optional[List[MessageEntity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None

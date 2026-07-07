from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

def build_keyboard(buttons_data: List[List[dict]]) -> Optional[InlineKeyboardMarkup]:
    """
    Builds a Pyrogram InlineKeyboardMarkup from a list of rows, 
    where each row is a list of button dictionaries.
    """
    if not buttons_data:
        return None
    
    keyboard = []
    for row_data in buttons_data:
        row = []
        for btn in row_data:
            text = btn.get("text", "")
            url = btn.get("url")
            callback_data = btn.get("callback_data")
            switch_inline_query = btn.get("switch_inline_query")
            user_id = btn.get("user_id")

            if url:
                row.append(InlineKeyboardButton(text, url=url))
            elif callback_data:
                row.append(InlineKeyboardButton(text, callback_data=callback_data))
            elif switch_inline_query is not None:
                row.append(InlineKeyboardButton(text, switch_inline_query=switch_inline_query))
            elif user_id:
                try:
                    row.append(InlineKeyboardButton(text, user_id=int(user_id)))
                except ValueError:
                    pass # Invalid user_id
            else:
                # Default to a safe callback if none provided
                row.append(InlineKeyboardButton(text, callback_data="none"))
        
        if row:
            keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard) if keyboard else None

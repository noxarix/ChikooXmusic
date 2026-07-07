import re
from typing import Tuple, Optional
from pyrogram.types import InlineKeyboardMarkup
from .keyboard import build_keyboard

def parse_buttons(text: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """
    Extract inline buttons from text using syntax like:
    ~ [Button, https://link]
    Returns cleaned text and InlineKeyboardMarkup if buttons exist.
    """
    lines = text.split("\n")
    clean_text_lines = []
    buttons_data = []

    button_row_regex = re.compile(r"^\s*~\s*(.+)$")
    button_regex = re.compile(r"\[([^,\]]+?)\s*,\s*([^\]]+?)\]")

    for line in lines:
        match = button_row_regex.match(line)
        if match:
            row_content = match.group(1)
            # Split by | for multiple buttons on the same row
            raw_buttons = row_content.split("|")
            current_row = []
            
            for raw_btn in raw_buttons:
                btn_match = button_regex.search(raw_btn)
                if btn_match:
                    btn_text = btn_match.group(1).strip()
                    target = btn_match.group(2).strip()
                    
                    btn_data = {"text": btn_text}
                    if target.startswith("callback:"):
                        btn_data["callback_data"] = target[len("callback:"):]
                    elif target.startswith("switch:"):
                        btn_data["switch_inline_query"] = target[len("switch:"):]
                    elif target.startswith("user:"):
                        btn_data["user_id"] = target[len("user:"):]
                    else:
                        # Assume it's a URL
                        if target.startswith("t.me/"):
                            target = "https://" + target
                        btn_data["url"] = target
                        
                    current_row.append(btn_data)
            
            if current_row:
                buttons_data.append(current_row)
        else:
            clean_text_lines.append(line)

    clean_text = "\n".join(clean_text_lines).strip()
    keyboard = build_keyboard(buttons_data)

    return clean_text, keyboard

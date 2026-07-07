from typing import Optional
from pyrogram.types import User, Chat

from .models import ParsedMessage
from .variables import variable_parser
from .buttons import parse_buttons
from .markdown import parse_markdown, parse_hyperlinks
from .html import parse_html
from .entities import build_entities

async def preview(text: str) -> ParsedMessage:
    """
    Preview mode: returns ParsedMessage without replacing variables,
    just to see how markdown, html, and buttons are formatted.
    """
    return await parse(text)

async def parse(
    text: str,
    user: Optional[User] = None,
    chat: Optional[Chat] = None,
    bot: Optional[User] = None
) -> ParsedMessage:
    """
    Main formatting pipeline.
    """
    if not text:
        return ParsedMessage(text="")

    try:
        # Step 1: Replace Variables
        text = variable_parser.parse(text, user=user, chat=chat, bot=bot)
        
        # Step 2: Extract Buttons
        text, reply_markup = parse_buttons(text)
        
        # Step 3: Parse Hyperlinks (Markdown)
        text = parse_hyperlinks(text)

        # Step 4: Parse custom Markdown to HTML
        text = parse_markdown(text)
        
        # Step 5: Parse HTML (Placeholder for any future sanitization)
        text = parse_html(text)

        # Step 6: Build Entities using Pyrogram's HTML Parser
        final_text, entities = await build_entities(text)
        
        return ParsedMessage(
            text=final_text,
            entities=entities,
            reply_markup=reply_markup
        )
    except Exception as e:
        # Gracefully handle errors and return raw text
        return ParsedMessage(text=text)

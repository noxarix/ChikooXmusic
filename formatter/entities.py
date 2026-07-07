from typing import List, Tuple
from pyrogram.parser.html import HTML
from pyrogram.types import MessageEntity

async def build_entities(text: str) -> Tuple[str, List[MessageEntity]]:
    """
    Takes a string containing HTML tags (converted from Markdown and standard HTML),
    and securely converts it into plain text and a list of Pyrogram MessageEntities 
    using Pyrogram's internal HTML parser.
    """
    parser = HTML(None)
    # Pyrogram 2.x HTML.parse() is an asynchronous method that returns a dict
    result = await parser.parse(text)
    
    parsed_text = result.get("message", text) if isinstance(result, dict) else result[0]
    entities = result.get("entities", []) if isinstance(result, dict) else result[1]
    
    return parsed_text, entities

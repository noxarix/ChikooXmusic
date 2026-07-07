import re

def parse_markdown(text: str) -> str:
    """
    Converts custom Rose/MissRose-style markdown to HTML tags.
    Supported:
    **Bold** -> <b>Bold</b>
    __Italic__ -> <i>Italic</i>
    ~~Strikethrough~~ -> <s>Strikethrough</s>
    --Underline-- -> <u>Underline</u>
    `Inline Code` -> <code>Inline Code</code>
    ```Code Block``` -> <pre>Code Block</pre>
    ||Spoiler|| -> <spoiler>Spoiler</spoiler>
    > Quote -> <blockquote>Quote</blockquote>
    """
    
    # Preformatted code blocks: ```code```
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    
    # Inline code: `code`
    text = re.sub(r'(?<!`)`([^`]+)`(?!`)', r'<code>\1</code>', text)
    
    # Block quotes
    text = re.sub(r'^>(.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    
    # Bold: **bold**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Underline: --underline--
    text = re.sub(r'--(.*?)--', r'<u>\1</u>', text)

    # Italic: __italic__
    text = re.sub(r'__(.*?)__', r'<i>\1</i>', text)
    
    # Strikethrough: ~~strike~~
    text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)
    
    # Spoiler: ||spoiler||
    text = re.sub(r'\|\|(.*?)\|\|', r'<spoiler>\1</spoiler>', text)
    
    return text

def parse_hyperlinks(text: str) -> str:
    """
    Converts markdown hyperlinks to HTML hyperlinks.
    [Text](URL) -> <a href="URL">Text</a>
    """
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

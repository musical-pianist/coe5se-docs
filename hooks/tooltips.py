# Each command word in a code block gets the VS Code extension's hover text as its title, which the
# theme's improved tooltips (content.tooltips) shows as a hover box. words.json is a copy of the
# extension's data/words.json.
import html
import json
import re
from pathlib import Path

WORDS = json.loads((Path(__file__).parent / "words.json").read_text(encoding="utf-8"))
SPAN = re.compile(r'<span class="([^"]*)">([+\-]?[a-z_][a-z_0-9.]*)</span>')
BLOCK = re.compile(r'<div class="([^"]*)highlight"><pre>.*?</pre></div>', re.S)


def hover_text(word):
    """The word's form, then what it does, from the first of its meanings."""
    entry = WORDS.get(word) or WORDS.get(word.lstrip("+-"))
    if not entry:
        return None
    doc = entry.get("doc") or next((d.get("doc", "") for d in entry.get("docs", [])), "")
    return f"{entry.get('signature', word)}\n\n{doc}".strip()


def titled(span):
    text = hover_text(span.group(2))
    if not text:
        return span.group(0)
    return f'<span class="{span.group(1)}" title="{html.escape(text, quote=True)}">{span.group(2)}</span>'


def on_page_content(content, page, config, files):
    def block(m):
        classes = m.group(1)
        if "language-" in classes and not re.search(r"language-c5(?:m|se)\b", classes):
            return m.group(0)   # another language's block (Lua): its words aren't .c5m words
        return SPAN.sub(titled, m.group(0))
    return BLOCK.sub(block, content)

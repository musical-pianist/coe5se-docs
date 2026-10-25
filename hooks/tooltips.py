# Each command word in a code block gets the VS Code extension's hover text as its title, which the
# theme's improved tooltips (content.tooltips) shows as a hover box, and so does each number the
# manual's number tables explain (newunits 28: Inferno). words.json and tables.json are copies of the
# extension's data/words.json and data/tables.json. On a noexplode line each part number gets the part
# of the addstring above it, read back as the extension reads it, and start and end their form.
import html
import json
import re
from pathlib import Path

WORDS = json.loads((Path(__file__).parent / "words.json").read_text(encoding="utf-8"))
TABLES = json.loads((Path(__file__).parent / "tables.json").read_text(encoding="utf-8"))
SPAN = re.compile(r'<span class="([^"]*)">([+\-]?[a-z_][a-z_0-9.]*)</span>')
NUMBER = re.compile(r'<span class="(m[a-z]*)">(-?\d+)</span>')
BLOCK = re.compile(r'<div class="([^"]*)highlight"><pre>.*?</pre></div>', re.S)
TAG = re.compile(r"<[^>]+>")
VALUE = re.compile(r'"[^"]*"?|\S+')


def hover_text(word):
    """The word's form, then what it does, from the first of its meanings."""
    entry = WORDS.get(word) or WORDS.get(word.lstrip("+-"))
    if not entry:
        return None
    doc = entry.get("doc") or next((d.get("doc", "") for d in entry.get("docs", [])), "")
    return f"{entry.get('signature', word)}\n{doc}".strip()


def title_attribute(text):
    """`text` as a title the theme's tooltip shows as written: the theme puts a title in as HTML, so it is
    escaped twice (once for the attribute, once for the HTML), or a form's <player> would vanish as a tag."""
    return html.escape(html.escape(text, quote=True), quote=True)


def titled(span):
    text = hover_text(span.group(2))
    if not text:
        return span.group(0)
    return f'<span class="{span.group(1)}" title="{title_attribute(text)}">{span.group(2)}</span>'


def argument_names(signature, word):
    """The names of a form's arguments, as the extension's parseSignature reads them."""
    body = re.split(r"[,;(]| or [a-z]", signature[signature.find(word) + len(word):])[0]
    names, either = [], False
    for m in re.finditer(r'\[([^\]]*)\]|"([^"]*)"|<([^>]*)>|(\|)', body):
        if m.group(4):
            either = True
            continue
        name = re.sub(r'[<>"]', "", next(g for g in m.groups()[:3] if g is not None)).strip()
        if either and names:
            names[-1] += " or " + name
        else:
            names.append(name)
        either = False
    return names


def number_meaning(word, index, value):
    """What the number at argument `index` of `word` means, by the extension's rules: the argument's
    name picks the table, or the word's own table for its first argument; a flags table adds up."""
    bare = word.lstrip("+-")
    entry = WORDS.get(word) or WORDS.get(bare)
    if not entry:
        return None
    docs = entry.get("docs") or []
    coe5se = entry.get("group") == "CoE5SE" or any(k.startswith("coe5se") for k in entry.get("kinds", []))
    signature = entry.get("signature") if coe5se or not docs else docs[0].get("signature")
    names = argument_names(signature or "", bare)
    if index >= len(names):
        return None
    key = TABLES["args"].get(names[index].lower()) or (TABLES["words"].get(bare) if index == 0 else None)
    table = TABLES["tables"].get(key)
    if not table:
        return None
    if table["flags"]:
        parts = [text for v, text in table["rows"] if int(value) & int(v)]
        meaning = " + ".join(parts)
    else:
        n = int(value)
        meaning = next((text for v, text in table["rows"]
                        if (lambda r: int(r.group(1)) <= n <= int(r.group(2)) if r else int(v) == n)(
                            re.fullmatch(r"(-?\d+)-(\d+)", v))), None)
    title_case = re.sub(r"\b[a-z]", lambda c: c.group(0).upper(), names[index])
    return f"{title_case} {value}: {meaning}\n{table['title']}" if meaning else None


def titled_numbers(line):
    """A code line with each number it explains titled: its place among the values after the line's
    first word picks the argument."""
    plain = html.unescape(TAG.sub("", line))
    first = re.match(r"\s*(\S+)", plain)
    if not first:
        return line
    word = first.group(1).removeprefix("#!@")
    starts = [m.start() for m in VALUE.finditer(plain, first.end())]
    out, pos, offset = [], 0, 0
    for m in NUMBER.finditer(line):
        offset += len(html.unescape(TAG.sub("", line[pos:m.start()])))
        index = next((i for i, s in enumerate(starts) if s == offset), None)
        text = number_meaning(word, index, m.group(2)) if index is not None else None
        out.append(line[pos:m.start()])
        out.append(f'<span class="{m.group(1)}" title="{title_attribute(text)}">{m.group(2)}</span>'
                   if text else m.group(0))
        offset += len(m.group(2))
        pos = m.end()
    return "".join(out) + line[pos:]


def first_word(line):
    """A code line's first word, its #!@ prefix left off, and its plain text."""
    plain = html.unescape(TAG.sub("", line))
    m = re.match(r"\s*(?:#!@)?\s*(\S+)", plain)
    return (m.group(1) if m else ""), plain


def part_meaning(string, value):
    """What part number `value` of a noexplode line names in `string`, the addstring above it."""
    if string is None:
        return "No addstring above it in this block."
    parts, n = string.split(" & "), int(value)
    if n < 1 or n > len(parts):
        return f"No part {value}: the string has {len(parts)}."
    part = parts[n - 1]
    count = re.sub(r"^\([^)]*\)", "", part).split("*")
    return f"Part {n}: {part}" + ("" if len(count) > 1 and "d" in count[0] else " (no dice)")


def form_meaning(value):
    """The noexplode form that names `value` (start or end)."""
    forms = (WORDS.get("noexplode") or {}).get("forms", [])
    form = next((f for f in forms if re.search(rf"\bnoexplode\s+{value}\b", f["signature"])), None)
    return form["doc"] if form else None


def titled_noexplode(line, string):
    """A noexplode line with its part numbers and its start or end titled."""
    def number(m):
        return f'<span class="{m.group(1)}" title="{title_attribute(part_meaning(string, m.group(2)))}">{m.group(2)}</span>'
    def word(m):
        text = form_meaning(m.group(2))
        return f'{m.group(1)}<span title="{title_attribute(text)}">{m.group(2)}</span>' if text else m.group(0)
    head, sep, rest = line.partition("noexplode")
    if rest.startswith("</span>"):   # the word's own span, when the lexer knows it
        sep, rest = sep + "</span>", rest[len("</span>"):]
    rest = NUMBER.sub(number, rest)
    rest = re.sub(r"(^\s*(?:<span[^>]*>)?)(start|end)\b", word, rest)
    return head + sep + rest


def on_page_content(content, page, config, files):
    def block(m):
        classes = m.group(1)
        if "language-" in classes and not re.search(r"language-c5(?:m|se)\b", classes):
            return m.group(0)   # another language's block (Lua): its words aren't .c5m words
        out, string = [], None   # string: the last addstring's text in the block the line is in
        for line in m.group(0).split("\n"):
            word, plain = first_word(line)
            if word == "addstring":
                quoted = re.search(r'"([^"]*)"?', plain)
                string = quoted.group(1) if quoted else None
            elif re.fullmatch(r"(?:new|select)\w+", word):
                string = None
            out.append(titled_noexplode(line, string) if word == "noexplode" else titled_numbers(line))
        return SPAN.sub(titled, "\n".join(out))
    return BLOCK.sub(block, content)

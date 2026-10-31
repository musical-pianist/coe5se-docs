"""Pygments lexers for CoE5 .c5m and CoE5SE .c5se files.

They read the TextMate grammars out of the CoE5 Modding VS Code extension itself,
coe5-modding.vsix in the folder MkDocs builds from (the site's root), so the docs
colour code the same way the editor does. gen_docs_commands.py in the CoE5SE
sources packs that .vsix there.
"""

import json
import re
import zipfile
from pathlib import Path

from pygments.lexer import Lexer
from pygments.token import Comment, Error, Keyword, Name, Number, Operator, String, Text

# First matching prefix wins, so longer scopes go before shorter ones.
SCOPE_TOKENS = [
    ("invalid.illegal", Error),
    ("comment", Comment.Single),
    ("string", String.Double),
    ("constant.numeric", Number),
    ("keyword.other.coe5se-line", Comment.Preproc),
    ("keyword.control.branch.if", Keyword.Branch.If),
    ("keyword.control.branch.elseif", Keyword.Branch.Elseif),   # its own colour: docs/stylesheets/site.css
    ("keyword.control.branch.else", Keyword.Branch.Else),
    ("keyword.operator", Operator),
    ("support.function", Name.Function),
    ("keyword", Keyword),
]


def token_for_scope(scope):
    for prefix, token in SCOPE_TOKENS:
        if scope and scope.startswith(prefix):
            return token
    return Text


def compile_rules(patterns):
    rules = []
    for pattern in patterns:
        if "match" in pattern:
            rules.append({
                "regex": re.compile(pattern["match"]),
                "scope": pattern.get("name"),
                "captures": pattern.get("captures", {}),
            })
        elif "begin" in pattern:
            rules.append({
                "regex": re.compile(pattern["begin"]),
                "scope": pattern.get("name"),
                "captures": pattern.get("beginCaptures", pattern.get("captures", {})),
                "end": re.compile(pattern["end"]),
                "rules": compile_rules(pattern.get("patterns", [])),
            })
    return rules


def emit_match(match, scope, captures, offset):
    """Yield the match's capture groups with their own scopes, the text between them with the rule's scope."""
    pos = match.start()
    groups = sorted(
        (match.start(int(group)), match.end(int(group)), spec.get("name"))
        for group, spec in captures.items()
        if group != "0" and match.group(int(group))
    )
    for start, end, group_scope in groups:
        if start < pos:
            continue
        if start > pos:
            yield offset + pos, token_for_scope(scope), match.string[pos:start]
        yield offset + start, token_for_scope(group_scope or scope), match.string[start:end]
        pos = end
    if pos < match.end():
        yield offset + pos, token_for_scope(scope), match.string[pos:match.end()]


def scan_line(line, pos, rules, scope, end, offset, out):
    """TextMate's rule: at each step the earliest match wins, ties go to the end pattern, then to the first rule."""
    while pos < len(line):
        best_start, best_rule, best_match = None, None, None
        if end:
            best_match = end.search(line, pos)
            if best_match:
                best_start = best_match.start()
        for rule in rules:
            match = rule["regex"].search(line, pos)
            if match and (best_start is None or match.start() < best_start):
                best_start, best_rule, best_match = match.start(), rule, match
        if best_match is None:
            break
        if best_start > pos:
            out.append((offset + pos, token_for_scope(scope), line[pos:best_start]))
        if best_rule is None:
            if best_match.group():
                out.append((offset + best_start, token_for_scope(scope), best_match.group()))
            return best_match.end()
        if best_match.end() == best_start and "end" not in best_rule:
            out.append((offset + best_start, token_for_scope(scope), line[best_start]))
            pos = best_start + 1
            continue
        out.extend(emit_match(best_match, best_rule["scope"] or scope, best_rule["captures"], offset))
        pos = best_match.end()
        if "end" in best_rule:
            pos = scan_line(line, pos, best_rule["rules"], best_rule["scope"] or scope, best_rule["end"], offset, out)
            if pos == best_start:
                out.append((offset + pos, token_for_scope(scope), line[pos]))
                pos += 1
    if pos < len(line):
        out.append((offset + pos, token_for_scope(scope), line[pos:]))
    return len(line)


class TextMateGrammarLexer(Lexer):
    grammar_file = None

    def __init__(self, **options):
        super().__init__(**options)
        with zipfile.ZipFile(Path.cwd() / "coe5-modding.vsix") as vsix:
            grammar = json.loads(vsix.read("extension/syntaxes/" + self.grammar_file))
        self.rules = compile_rules(grammar["patterns"])

    def get_tokens_unprocessed(self, text):
        offset = 0
        for line in text.splitlines(keepends=True):
            out = []
            scan_line(line, 0, self.rules, None, None, offset, out)
            yield from out
            offset += len(line)


class C5mLexer(TextMateGrammarLexer):
    name = "CoE5 mod"
    aliases = ["c5m"]
    filenames = ["*.c5m"]
    grammar_file = "c5m.tmLanguage.json"


class C5seLexer(TextMateGrammarLexer):
    name = "CoE5SE mod"
    aliases = ["c5se"]
    filenames = ["*.c5se"]
    grammar_file = "c5se.tmLanguage.json"

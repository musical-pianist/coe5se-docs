# Each entry heading with a New label gets the same label in the page's table of contents, on the right,
# so a reader sees what is new on the page at a glance (scripts/gen_docs_commands.py in the CoE5SE
# sources puts the label on the heading).
import re

NEW_LABEL = '<span class="new-badge">New</span>'
NEW_HEADING = re.compile(r'<h3 [^>]*\bid="([^"]+)"[^>]*>[^<]*' + re.escape(NEW_LABEL))   # an entry heading also has class="command"


def entry_labels(output, page, config):
    for anchor in set(NEW_HEADING.findall(output)):
        link = re.compile(r'(<a href="#' + re.escape(anchor) + r'" class="md-nav__link[^"]*">\s*<span class="md-ellipsis">\s*)([^<]*?)(\s*</span>)')
        output = link.sub(lambda m: f"{m.group(1)}{m.group(2)} {NEW_LABEL}{m.group(3)}", output)
    return output


# A nav group the reader hasn't opened (Spells, Monsters, Mod Setup) shows the New status of a page inside it on
# its own label, so a new page is never hidden in a closed group.
NEW_STATUS = '<span class="md-status md-status--new" title="Recently added"></span>'
GROUP_LABEL = re.compile(r'(<label class="md-nav__link" for="([^"]+)" id="[^"]+"[^>]*>.*?)(<span class="md-nav__icon md-icon"></span>\s*</label>)', re.S)


def group_nav(output, label_id):
    """The group's own nav, from its aria-labelledby to its closing tag, or ""."""
    start = output.find(f'aria-labelledby="{label_id}"')
    if start < 0:
        return ""
    depth, i = 0, output.rfind("<nav", 0, start)
    for m in re.finditer(r"<nav\b|</nav>", output[i:]):
        depth += 1 if m.group(0) == "<nav" else -1
        if depth == 0:
            return output[i:i + m.end()]
    return ""


def on_post_page(output, page, config):
    output = entry_labels(output, page, config)   # the entry headings' labels in the page's contents first
    def mark(m):
        nav = group_nav(output, m.group(2) + "_label")
        if "md-status--new" in m.group(1) or "md-status--new" not in nav or 'data-md-level="1"' in nav[:200]:
            return m.group(0)   # already marked, nothing new inside, or a top section, which is always open
        return m.group(1) + NEW_STATUS + m.group(3)
    return GROUP_LABEL.sub(mark, output)

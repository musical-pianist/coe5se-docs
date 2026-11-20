# A page whose front matter says "needs_work: true" opens with the Needs work box, and its nav link carries a
# Needs work status icon, beside its New status when it has one. Material's own status takes one value per page, and
# New already uses it, so the label is added here. The marked pages are read from the sources at each build,
# since a --dirty rebuild reads only the pages that changed.
import re
from pathlib import Path

from mkdocs.utils import get_relative_url
from mkdocs.utils.meta import get_data

LABEL = '<span class="md-status md-status--needs-work" title="Needs work"></span>'   # a status icon like New's, its name on hover
BOX = (
    '!!! warning "Needs work"\n'
    '    This page is declared as "Needs Work". All commands below are working and underwent standard testing, but '
    "the script extender modder recognizes this list is rough and probably won't make for a great time if you use them.\n"
    "\n"
    "    You can make plans around these commands and place them in mods, and they will still work after a rework, "
    "but expect this page to be dramatically refined as time progresses.\n"
)
FIRST_HEADING = re.compile(r"^# .*\n", re.M)

marked = set()   # the marked pages' URLs


def on_pre_build(config):
    marked.clear()
    docs = Path(config["docs_dir"])
    for path in docs.rglob("*.md"):
        _, meta = get_data(path.read_text(encoding="utf-8"))
        if meta.get("needs_work"):
            uri = path.relative_to(docs).as_posix()
            marked.add(uri[:-len("index.md")] if uri.endswith("index.md") else uri[:-3] + "/")


def on_page_markdown(markdown, page, config, files):
    if not page.meta.get("needs_work"):
        return markdown
    m = FIRST_HEADING.search(markdown)
    at = m.end() if m else 0
    return markdown[:at] + "\n" + BOX + "\n" + markdown[at:]


def on_post_page(output, page, config):
    for url in marked:
        href = re.escape(get_relative_url(url, page.url))
        link = re.compile(r'(<a href="' + href + r'" class="md-nav__link[^"]*">\s*<span class="md-ellipsis">[^<]*?)(\s*</span>)')
        output = link.sub(lambda m: m.group(1) + m.group(2) + LABEL, output)   # after the title, where Material puts New
    return output

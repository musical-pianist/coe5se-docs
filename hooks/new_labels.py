# Each entry heading with a New label gets the same label in the page's table of contents, on the right,
# so a reader sees what is new on the page at a glance (scripts/gen_docs_commands.py in the CoE5SE
# sources puts the label on the heading).
import re

NEW_LABEL = '<span class="new-badge">New</span>'
NEW_HEADING = re.compile(r'<h3 id="([^"]+)">[^<]*' + re.escape(NEW_LABEL))


def on_post_page(output, page, config):
    for anchor in set(NEW_HEADING.findall(output)):
        link = re.compile(r'(<a href="#' + re.escape(anchor) + r'" class="md-nav__link">\s*<span class="md-ellipsis">\s*)([^<]*?)(\s*</span>)')
        output = link.sub(lambda m: f"{m.group(1)}{m.group(2)} {NEW_LABEL}{m.group(3)}", output)
    return output

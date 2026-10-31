# Fails the build when a command entry heading (class "command", a purple line in the page's table of
# contents) has no version: data-added="<major.minor>", the CoE5SE release it came in, which
# scripts/gen_docs_commands.py in the CoE5SE sources puts on it from the heading's added=. Without it the
# entry's New label could be skipped (Jacob: "Never ever ever should they not have version tag").
import re

from mkdocs.exceptions import PluginError

COMMAND_HEADING = re.compile(r'<h3 (?=[^>]*\bclass="command")[^>]*\bid="([^"]+)"[^>]*>')
VERSION = re.compile(r'\bdata-added="\d+\.\d+"')


def on_post_page(output, page, config):
    missing = [m.group(1) for m in COMMAND_HEADING.finditer(output) if not VERSION.search(m.group(0))]
    if missing:
        raise PluginError(f"command_versions: {page.file.src_uri}: command entries with no version "
                          f"(added= in the CoE5SE sources' docs/commands-page/): {', '.join('#' + a for a in missing)}")
    return output

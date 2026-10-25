# Each command's entry heading (class "command", which scripts/gen_docs_commands.py in the CoE5SE sources
# puts on it) gets its line in the page's table of contents, on the right, marked too, so the site's CSS
# can colour the commands apart from the examples and other headings.
import re

COMMAND_HEADING = re.compile(r'<h3 (?=[^>]*\bclass="command")[^>]*\bid="([^"]+)"')


def on_post_page(output, page, config):
    for anchor in set(COMMAND_HEADING.findall(output)):
        output = output.replace(f'<a href="#{anchor}" class="md-nav__link">', f'<a href="#{anchor}" class="md-nav__link command-link">')
    return output

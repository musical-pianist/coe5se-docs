# Each command's entry heading (class "command", which scripts/gen_docs_commands.py in the CoE5SE sources
# puts on it) gets its line in the page's table of contents, on the right, marked too, so the site's CSS
# can colour the commands apart from the examples and other headings. An entry that is one table
# (data-toc-rows) gets a line for each command its rows name in place of its own line.
import re

COMMAND_HEADING = re.compile(r'<h3 (?=[^>]*\bclass="command")[^>]*\bid="([^"]+)"')
TABLE_HEADING = re.compile(r'<h3 (?=[^>]*\bdata-toc-rows="([^"]+)")[^>]*\bid="([^"]+)"')
NEW_BADGE = re.compile(r'<span class="new-badge">.*?</span>')


def list_table_rows(rows, badge):
    return "".join(f'<li class="md-nav__item"><a href="#{row}" class="md-nav__link command-link">'
                   f'<span class="md-ellipsis">{row}{badge}</span></a></li>' for row in rows.split())


def on_post_page(output, page, config):
    for anchor in set(COMMAND_HEADING.findall(output)):
        output = output.replace(f'<a href="#{anchor}" class="md-nav__link">', f'<a href="#{anchor}" class="md-nav__link command-link">')
    for rows, anchor in set(TABLE_HEADING.findall(output)):
        line = re.compile(rf'<li class="md-nav__item">\s*<a href="#{anchor}" class="md-nav__link command-link">.*?</a>\s*</li>', re.S)

        def replace_line(match):
            badge = NEW_BADGE.search(match.group(0))
            return list_table_rows(rows, " " + badge.group(0) if badge else "")

        output = line.sub(replace_line, output)
    return output

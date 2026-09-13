"""Convert the Markdown features needed by this encyclopedia into safe HTML."""

import html
import re
from urllib.parse import urlsplit


HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
LIST_ITEM = re.compile(r"^\s*[-*+]\s+(.+)$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD = re.compile(r"(\*\*|__)(.+?)\1")


def _bold(text):
    escaped = html.escape(text)
    return BOLD.sub(lambda match: f"<strong>{match.group(2)}</strong>", escaped)


def _safe_url(url):
    parts = urlsplit(url)
    return not parts.scheme or parts.scheme.lower() in {"http", "https", "mailto"}


def _inline(text):
    rendered = []
    position = 0
    for match in LINK.finditer(text):
        rendered.append(_bold(text[position:match.start()]))
        label, url = match.groups()
        if _safe_url(url):
            rendered.append(
                f'<a href="{html.escape(url, quote=True)}">{_bold(label)}</a>'
            )
        else:
            rendered.append(html.escape(match.group(0)))
        position = match.end()
    rendered.append(_bold(text[position:]))
    return "".join(rendered)


def markdown_to_html(source):
    """Render headings, bold text, unordered lists, links, and paragraphs."""
    blocks = []
    paragraph = []
    list_items = []

    def flush_paragraph():
        if paragraph:
            blocks.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list():
        if list_items:
            items = "".join(f"<li>{_inline(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items.clear()

    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading = HEADING.match(stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue

        item = LIST_ITEM.match(line)
        if item:
            flush_paragraph()
            list_items.append(item.group(1))
            continue

        flush_list()
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)

import random
import re

from django.shortcuts import redirect, render

from . import util
from .markdown import markdown_to_html


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f'The page "{title}" was not found.'
        }, status=404)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content_html": markdown_to_html(content)
    })


def search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return redirect("index")

    entries = util.list_entries()
    exact_match = next(
        (title for title in entries if title.casefold() == query.casefold()),
        None
    )
    if exact_match is not None:
        return redirect("entry", title=exact_match)

    results = [title for title in entries if query.casefold() in title.casefold()]
    return render(request, "encyclopedia/search_results.html", {
        "query": query,
        "results": results
    })


def new_page(request):
    title = ""
    content = ""
    error = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")

        if not title or not content.strip():
            error = "Enter both a title and some Markdown content."
        elif re.search(r'[<>:"/\\|?*\x00-\x1f]', title):
            error = "The title contains a character that cannot be used in a page name."
        elif any(existing.casefold() == title.casefold()
                 for existing in util.list_entries()):
            error = "A page with this title already exists."
        else:
            util.save_entry(title, content)
            return redirect("entry", title=title)

    return render(request, "encyclopedia/new_page.html", {
        "title": title,
        "content": content,
        "error": error
    })


def edit_page(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f'The page "{title}" was not found.'
        }, status=404)

    if request.method == "POST":
        content = request.POST.get("content", "")
        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": content
    })


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "There are no pages to visit yet."
        }, status=404)
    return redirect("entry", title=random.choice(entries))

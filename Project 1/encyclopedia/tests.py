from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .markdown import markdown_to_html


@override_settings(ALLOWED_HOSTS=["testserver"])
class WikiViewsTests(SimpleTestCase):
    @patch("encyclopedia.views.util.list_entries", return_value=["HTML", "Python"])
    def test_index_links_to_entries(self, _entries):
        response = self.client.get(reverse("index"))
        self.assertContains(response, 'href="/wiki/Python"')

    @patch("encyclopedia.views.util.get_entry", return_value="# Python\n\n**Useful** language")
    def test_entry_renders_markdown(self, _entry):
        response = self.client.get(reverse("entry", args=["Python"]))
        self.assertContains(response, "<h1>Python</h1>", html=True)
        self.assertContains(response, "<strong>Useful</strong>", html=True)
        self.assertContains(response, 'href="/wiki/Python/edit"')

    @patch("encyclopedia.views.util.get_entry", return_value=None)
    def test_missing_entry_shows_error(self, _entry):
        response = self.client.get(reverse("entry", args=["Missing"]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "was not found", status_code=404)

    @patch("encyclopedia.views.util.list_entries", return_value=["HTML", "Python"])
    def test_search_exact_and_partial(self, _entries):
        exact = self.client.get(reverse("search"), {"q": "python"})
        self.assertRedirects(exact, reverse("entry", args=["Python"]), fetch_redirect_response=False)
        partial = self.client.get(reverse("search"), {"q": "yth"})
        self.assertContains(partial, 'href="/wiki/Python"')
        self.assertNotContains(partial, 'href="/wiki/HTML"')

    @patch("encyclopedia.views.util.save_entry")
    @patch("encyclopedia.views.util.list_entries", return_value=["Python"])
    def test_new_page_rejects_duplicate(self, _entries, save):
        response = self.client.post(reverse("new_page"), {
            "title": "python", "content": "# Another page"
        })
        self.assertContains(response, "already exists")
        save.assert_not_called()

    @patch("encyclopedia.views.util.save_entry")
    @patch("encyclopedia.views.util.list_entries", return_value=[])
    def test_new_page_saves_and_redirects(self, _entries, save):
        response = self.client.post(reverse("new_page"), {
            "title": "New Topic", "content": "# New Topic"
        })
        save.assert_called_once_with("New Topic", "# New Topic")
        self.assertRedirects(response, reverse("entry", args=["New Topic"]), fetch_redirect_response=False)

    @patch("encyclopedia.views.util.save_entry")
    @patch("encyclopedia.views.util.get_entry", return_value="# Python")
    def test_edit_prefills_and_saves(self, _entry, save):
        url = reverse("edit_page", args=["Python"])
        self.assertContains(self.client.get(url), "# Python")
        response = self.client.post(url, {"content": "# Updated"})
        save.assert_called_once_with("Python", "# Updated")
        self.assertRedirects(response, reverse("entry", args=["Python"]), fetch_redirect_response=False)

    @patch("encyclopedia.views.random.choice", return_value="Python")
    @patch("encyclopedia.views.util.list_entries", return_value=["Python", "HTML"])
    def test_random_page_redirects(self, _entries, choice):
        response = self.client.get(reverse("random_page"))
        choice.assert_called_once()
        self.assertRedirects(response, reverse("entry", args=["Python"]), fetch_redirect_response=False)


class MarkdownTests(SimpleTestCase):
    def test_required_markdown_and_unsafe_html(self):
        output = markdown_to_html(
            "# Heading\n\nA **bold** [link](https://example.com).\n\n- one\n- two\n\n<script>x</script>"
        )
        self.assertIn("<h1>Heading</h1>", output)
        self.assertIn("<strong>bold</strong>", output)
        self.assertIn('<a href="https://example.com">link</a>', output)
        self.assertIn("<ul><li>one</li><li>two</li></ul>", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<a href=\"javascript:", markdown_to_html("[bad](javascript:alert)"))

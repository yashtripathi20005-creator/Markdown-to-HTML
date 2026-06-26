
---

### `tests.py` (optional, for verification)
```python
import unittest
from converter import MarkdownToHTML

class TestMarkdownToHTML(unittest.TestCase):
    def setUp(self):
        self.converter = MarkdownToHTML()

    def test_headings(self):
        self.assertEqual(self.converter.convert("# Heading"), "<h1>Heading</h1>")
        self.assertEqual(self.converter.convert("## Heading 2"), "<h2>Heading 2</h2>")

    def test_bold(self):
        self.assertEqual(self.converter.convert("**bold**"), "<p><strong>bold</strong></p>")
        self.assertEqual(self.converter.convert("__bold__"), "<p><strong>bold</strong></p>")

    def test_italic(self):
        self.assertEqual(self.converter.convert("*italic*"), "<p><em>italic</em></p>")
        self.assertEqual(self.converter.convert("_italic_"), "<p><em>italic</em></p>")

    def test_inline_code(self):
        self.assertEqual(self.converter.convert("`code`"), "<p><code>code</code></p>")

    def test_link(self):
        result = self.converter.convert("[Google](https://google.com)")
        self.assertIn('<a href="https://google.com">Google</a>', result)

    def test_image(self):
        result = self.converter.convert("![alt](image.jpg)")
        self.assertIn('<img src="image.jpg" alt="alt" />', result)

    def test_unordered_list(self):
        md = "- item1\n- item2"
        result = self.converter.convert(md)
        self.assertIn("<ul>", result)
        self.assertIn("<li>item1</li>", result)
        self.assertIn("<li>item2</li>", result)
        self.assertIn("</ul>", result)

    def test_ordered_list(self):
        md = "1. first\n2. second"
        result = self.converter.convert(md)
        self.assertIn("<ol>", result)
        self.assertIn("<li>first</li>", result)
        self.assertIn("<li>second</li>", result)
        self.assertIn("</ol>", result)

    def test_blockquote(self):
        md = "> quote line"
        result = self.converter.convert(md)
        self.assertIn("<blockquote>", result)
        self.assertIn("quote line", result)
        self.assertIn("</blockquote>", result)

    def test_code_block(self):
        md = "```\ndef foo():\n    pass\n```"
        result = self.converter.convert(md)
        self.assertIn("<pre><code>", result)
        self.assertIn("def foo():", result)
        self.assertIn("</code></pre>", result)

    def test_horizontal_rule(self):
        self.assertEqual(self.converter.convert("---"), "<hr />")
        self.assertEqual(self.converter.convert("***"), "<hr />")

if __name__ == "__main__":
    unittest.main()

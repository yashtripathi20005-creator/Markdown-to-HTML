import re
import sys
from typing import List, Tuple

class MarkdownToHTML:
    def __init__(self):
        self.html_output = []
        self.in_list = False
        self.list_type = None
        self.in_blockquote = False
        self.blockquote_content = []

    def convert(self, markdown_text: str) -> str:
        lines = markdown_text.split('\n')
        self.html_output = []
        self.in_list = False
        self.list_type = None
        self.in_blockquote = False
        self.blockquote_content = []

        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Handle blank lines to close open containers
            if line.strip() == '':
                if self.in_list:
                    self._close_list()
                if self.in_blockquote:
                    self._close_blockquote()
                self.html_output.append('')
                i += 1
                continue

            # Check for blockquote
            if line.lstrip().startswith('> '):
                self._handle_blockquote(lines, i)
                i += 1
                # Skip the lines consumed by blockquote
                while i < len(lines) and lines[i].lstrip().startswith('> '):
                    i += 1
                continue

            # Check for headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                if self.in_list:
                    self._close_list()
                if self.in_blockquote:
                    self._close_blockquote()
                level = len(heading_match.group(1))
                content = self._parse_inline(heading_match.group(2))
                self.html_output.append(f'<h{level}>{content}</h{level}>')
                i += 1
                continue

            # Check for unordered list
            ul_match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            if ul_match:
                if not self.in_list:
                    self._close_blockquote()
                    self.html_output.append('<ul>')
                    self.in_list = True
                    self.list_type = 'ul'
                indent = len(ul_match.group(1))
                content = self._parse_inline(ul_match.group(2))
                self.html_output.append(f'  <li>{content}</li>')
                i += 1
                continue

            # Check for ordered list
            ol_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
            if ol_match:
                if not self.in_list:
                    self._close_blockquote()
                    self.html_output.append('<ol>')
                    self.in_list = True
                    self.list_type = 'ol'
                content = self._parse_inline(ol_match.group(3))
                self.html_output.append(f'  <li>{content}</li>')
                i += 1
                continue

            # Check for horizontal rule
            if re.match(r'^(\s*)([-*_]){3,}(\s*)$', line):
                if self.in_list:
                    self._close_list()
                if self.in_blockquote:
                    self._close_blockquote()
                self.html_output.append('<hr />')
                i += 1
                continue

            # Check for code block (fenced with ```)
            if line.strip().startswith('```'):
                if self.in_list:
                    self._close_list()
                if self.in_blockquote:
                    self._close_blockquote()
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # Skip the closing ```
                code_content = '\n'.join(code_lines)
                self.html_output.append(f'<pre><code>{self._escape_html(code_content)}</code></pre>')
                continue

            # Regular paragraph
            if self.in_list:
                self._close_list()
            if self.in_blockquote:
                self._close_blockquote()
            content = self._parse_inline(line)
            self.html_output.append(f'<p>{content}</p>')
            i += 1

        # Close any open containers at the end
        if self.in_list:
            self._close_list()
        if self.in_blockquote:
            self._close_blockquote()

        return '\n'.join(self.html_output)

    def _handle_blockquote(self, lines: List[str], start_idx: int):
        if self.in_list:
            self._close_list()
        self.in_blockquote = True
        self.blockquote_content = []
        i = start_idx
        while i < len(lines) and lines[i].lstrip().startswith('> '):
            line = lines[i].lstrip()[2:]  # Remove '> '
            self.blockquote_content.append(line)
            i += 1
        # Convert the blockquote content recursively
        blockquote_md = '\n'.join(self.blockquote_content)
        blockquote_html = self.convert(blockquote_md)
        self.html_output.append(f'<blockquote>\n{blockquote_html}\n</blockquote>')
        self.in_blockquote = False
        self.blockquote_content = []

    def _close_list(self):
        if self.in_list:
            if self.list_type == 'ul':
                self.html_output.append('</ul>')
            elif self.list_type == 'ol':
                self.html_output.append('</ol>')
            self.in_list = False
            self.list_type = None

    def _close_blockquote(self):
        if self.in_blockquote:
            self.in_blockquote = False
            self.blockquote_content = []

    def _parse_inline(self, text: str) -> str:
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Inline code: `text`
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', text)
        
        # Escape remaining HTML characters
        return self._escape_html(text, skip_links=False)

    def _escape_html(self, text: str, skip_links: bool = True) -> str:
        # For code blocks, escape everything
        if skip_links:
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
        else:
            # For inline, we need to be careful with already generated tags
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
        return text


def convert_file(input_file: str, output_file: str = None):
    """Convert a markdown file to HTML."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    converter = MarkdownToHTML()
    html_output = converter.convert(markdown_text)
    
    # Add basic HTML structure if output is a full page
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Markdown</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; margin-left: 0; color: #555; }}
    </style>
</head>
<body>
{html_output}
</body>
</html>"""
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"HTML successfully written to {output_file}")
    else:
        print(full_html)


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.md> [output.html]")
        print("If output file is not specified, HTML will be printed to stdout.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_file(input_file, output_file)


if __name__ == "__main__":
    main()

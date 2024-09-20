# Add "markdown_it" jinja2 filter,
# based on https://github.com/executablebooks/markdown-it-py
from markdown_it import MarkdownIt
#from mdit_py_plugins.front_matter import front_matter_plugin
#from mdit_py_plugins.footnote import footnote_plugin

from jinja2.utils import markupsafe
from root import app


md = (
    MarkdownIt()
)


@app.template_filter('markdown_it')
def markdown_it_filter(text):
    if text is None:
        return ''

    html_text = md.render(text)

    return markupsafe.Markup(html_text)

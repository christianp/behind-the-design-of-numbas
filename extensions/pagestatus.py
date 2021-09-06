from typing import Any, Dict, List, Tuple, cast

from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

import sphinx
from sphinx.application import Sphinx
from sphinx.util import logging, texescape
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from sphinx.writers.html import HTMLTranslator
from sphinx.writers.latex import LaTeXTranslator

logger = logging.getLogger(__name__)


class page_status_node(nodes.Admonition, nodes.Element):
    pass

page_status_texts = {
    'outline': {'title': 'Outline', 'explanation': '''This is a rough outline of an article. It might not use full sentences everywhere and probably won't make much sense at the moment.'''},
    'in-progress': {'title': 'In progress', 'explanation': '''This article is still being written. Some sections are incomplete, and it hasn't been proofread.'''},
    'draft': {'title': 'Draft', 'explanation': '''This article is pretty much complete, but needs to be proofread and might change.'''},
    'finished': {'title': 'Finished', 'explanation': '''This article is finished. If you spot a mistake or have a question, please let us know.'''},
}

def page_status_kind(argument):
    return directives.choice(argument, page_status_texts.keys())


class PageStatus(BaseAdmonition, SphinxDirective):
    """
    A page_status entry, displayed (if configured) in the form of an admonition.
    """

    node_class = page_status_node
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: OptionSpec = {
        'class': directives.class_option,
        'name': directives.unchanged,
        'kind': page_status_kind,
    }

    def assert_has_content(self):
        pass

    def run(self) -> List[Node]:
        if not self.options.get('class'):
            self.options['class'] = ['admonition-page-status']

        (status,) = super().run()  # type: Tuple[Node]
        if isinstance(status, nodes.system_message):
            return [status]
        elif isinstance(status, page_status_node):
            text = page_status_texts[self.options['kind']]
            status.insert(0, nodes.title(text=f"Page status: {text['title']}"))
            status.insert(1, nodes.paragraph(text=text['explanation']))
            status['docname'] = self.env.docname
            self.add_name(status)
            self.set_source_info(status)
            self.state.document.note_explicit_target(status)
            return [status]
        else:
            raise RuntimeError  # never reached here


def visit_page_status_node(self: HTMLTranslator, node: page_status_node) -> None:
    self.visit_admonition(node)


def depart_page_status_node(self: HTMLTranslator, node: page_status_node) -> None:
    self.depart_admonition(node)


def latex_visit_page_status_node(self: LaTeXTranslator, node: page_status_node) -> None:
    self.body.append('\n\\begin{sphinxadmonition}{note}{')
    self.body.append(self.hypertarget_to(node))

    title_node = cast(nodes.title, node[0])
    title = texescape.escape(title_node.astext(), self.config.latex_engine)
    self.body.append('%s:}' % title)
    node.pop(0)


def latex_depart_page_status_node(self: LaTeXTranslator, node: page_status_node) -> None:
    self.body.append('\\end{sphinxadmonition}\n')


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_event('page_status-defined')

    app.add_node(page_status_node,
                 html=(visit_page_status_node, depart_page_status_node),
                 latex=(latex_visit_page_status_node, latex_depart_page_status_node),
                 text=(visit_page_status_node, depart_page_status_node),
                 man=(visit_page_status_node, depart_page_status_node),
                 texinfo=(visit_page_status_node, depart_page_status_node))

    app.add_directive('page_status', PageStatus)
    return {
        'version': sphinx.__display_version__,
        'env_version': 2,
        'parallel_read_safe': True
    }


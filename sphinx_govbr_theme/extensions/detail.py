from docutils import nodes
from docutils.parsers.rst import Directive, directives

from myst_parser.parsers.docutils_ import Parser as MystParser


class BrDetail(nodes.General, nodes.Element):
    pass


class BrDetailDirective(Directive):
    has_content = True

    option_spec = {
        "title": directives.unchanged_required,
        "group": directives.unchanged,
    }

    def run(self):
        container = BrDetail()

        container["title"] = self.options.get("title")
        container["group"] = self.options.get("group")

        content_node = nodes.section()

        self.state.nested_parse(
            self.content,
            self.content_offset,
            content_node,
        )

        container += content_node

        return [container]

def visit_detail_html(self, node):
    name_att = ''
    group = node.get("group")
    if group:
        name_att = f'name="{self.encode(group)}" '
    self.body.append(f'<details {name_att}class="br_detail br_component">')

    title = node.get("title", "Untitled")
    if title:
        self.body.append(
            f'<summary>{self.encode(title)}</summary>'
        )


def depart_detail_html(self, node):
    self.body.append("</details>")

def setup_detail(app):
    app.add_node(BrDetail, html=(visit_detail_html, depart_detail_html))
    app.add_directive("br_detail", BrDetailDirective)

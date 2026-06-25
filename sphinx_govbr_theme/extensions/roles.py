from docutils import nodes
from sphinx.roles import XRefRole
from sphinx.addnodes import pending_xref

class BrLinkRole(XRefRole):
    """
    Usage:

        :br_link:`Title <target>`
        :br_link:`target`

    Behaves like :ref:, but uses the Design System's button CSS
    to the generated hyperlink.
    """

    def result_nodes(self, document, env, node, is_ref):
        node_list, messages = super().result_nodes(
            document, env, node, is_ref
        )

        for n in node_list:
            if isinstance(n, nodes.reference) or isinstance(n, pending_xref):
                n["classes"].append("br_component")
                n["reftype"] = 'ref'
                n["refdomain"] = 'std'

        return node_list, messages

def br_open_accordion(
    name,
    rawtext,
    text,
    lineno,
    inliner,
    options=None,
    content=None,
):
    node = nodes.raw(
        "",
        f'<details class="br_detail"><summary class="h3">{text}</summary>',
        format="html",
    )

    return [node], []

def br_close_accordion(
    name,
    rawtext,
    text,
    lineno,
    inliner,
    options=None,
    content=None,
):
    node = nodes.raw(
        "",
        '</details>',
        format="html",
    )

    return [node], []

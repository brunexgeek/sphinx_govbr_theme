from sphinx.writers.html5 import HTML5Translator
from docutils import nodes
from sphinx.locale import _

def is_govbr_component(node):
    return 'br_component' in node['classes']

class DesignSystemTranslator(HTML5Translator):

    def visit_admonition(self, node, name=''):
        DANGER = ['danger', 'fa-times-circle']
        INFO = ['info', 'fa-info-circle']
        WARNING = ['warning', 'fa-exclamation-triangle']
        MAPPING = {
            'attention' : WARNING,
            'caution'   : WARNING,
            'danger'    : DANGER,
            'error'     : DANGER,
            'hint'      : INFO,
            'important' : WARNING,
            'note'      : INFO,
            'tip'       : INFO,
            'warning'   : WARNING,
        }

        if name not in MAPPING:
            name = 'tip'

        self.body.append(
            f'<div class="br-message {MAPPING[name][0]}">'
            f'<div class="icon"><i aria-hidden="true" class="fas fa-lg {MAPPING[name][1]}"></i></div>'
            '<div class="content" role="alert">'
        )

    def depart_admonition(self, node):
        self.body.append('</div></div>')

    def visit_reference(self, node):
        if is_govbr_component(node):
            uri = node.get("refuri")

            # internal reference fallback
            if uri is None and "refid" in node:
                uri = f"#{node['refid']}"
            text = node.astext()

            self.body.append(
                f'<a href="{uri}" class="br-button secondary">'
                f'<span class="ml-2">{text}</span>'
            )
            raise nodes.SkipChildren
        else:
            super().visit_reference(node)

    def depart_reference(self, node):
        if is_govbr_component(node):
            self.body.append("</span></a>")
        else:
            super().depart_reference(node)

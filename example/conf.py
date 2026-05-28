from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

coverage_statistics_to_report = coverage_statistics_to_stdout = True

project = 'Padrão Digital de Governo'
project_subtitle = 'Design System | Versão 3.7.0'
copyright = '2026, Governo Federal'
language = 'pt_BR'
release = version = "3.7.0"
show_authors = True
nitpicky = True
show_warning_types = True

extensions = ["myst_parser"]
myst_enable_extensions = ["substitution"]
myst_substitutions = {
    "project": project,
}

html_theme = 'sphinx_govbr_theme'
modindex_common_prefix = ['sphinx.']
html_static_path = ['_static']
html_copy_source = False
html_last_updated_fmt = '%Y-%m-%d'
html_use_index = False
html_baseurl = os.environ.get("HTML_BASEURL", 'http://localhost:8000/')
html_permalinks_icon = '<i class="fas fa-link" aria-hidden="true"></i>'
html_theme_options = {
    'show_child_topics': True,
    'show_parent_topic': True,
    'toc_only_pages' : False,
    'signature' : 'Governo Federal',
    'header_extra_links': [
        {
            'title': 'Design System do gov.br',
            'url': 'https://www.gov.br/ds/home'
        },
        {
            'title': 'PPSI do Governo Digital',
            'url': 'https://www.gov.br/governodigital/pt-br/privacidade-e-seguranca/ppsi-2.0'
        }
    ],
    'footer_statement' : """This example documentation uses some content from Wikipedia. Wikipedia is hosted by the Wikimedia Foundation, a non-profit organization that also hosts a range of other projects. Text is available under the Creative Commons Attribution-ShareAlike 4.0 License; additional terms may apply.""",
    'project_subtitle' : project_subtitle
}

gettext_compact = False

def setup(app: Sphinx) -> None:
    pass


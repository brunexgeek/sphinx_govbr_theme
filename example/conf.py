from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

coverage_statistics_to_report = coverage_statistics_to_stdout = True

project = 'Amazônia Brasileira'
project_subtitle = 'O que há de mas belo no mundo vem da natureza'
copyright = '2026, sphinx-govbr-theme'
language = 'pt_BR'
release = version = "1.0.0"
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
html_baseurl = os.environ.get("HTML_BASEURL", 'http://127.0.0.1:8000/')
html_permalinks_icon = '<i class="fas fa-link" aria-hidden="true"></i>'
html_theme_options = {
    'show_child_topics': True,
    'show_parent_topic': True,
    'toc_only_pages' : False,
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
    'project_subtitle' : project_subtitle,
    'base_url' : html_baseurl
}

gettext_compact = False

def setup(app: Sphinx) -> None:
    pass


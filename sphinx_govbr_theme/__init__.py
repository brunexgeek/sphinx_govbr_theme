from .toc import setup as setup_toc
import os
import re
import json
from sphinx.util import logging
from sphinx.util.console import colorize
import time
from datetime import datetime
from .translator import DesignSystemTranslator
from .extensions import setup as setup_extensions
from docutils import nodes
from urllib.parse import urljoin
from pathlib import Path
from .util import normalize_path

logger = logging.getLogger(__name__)

def _on_doctree_resolved(app, doctree, docname):
    """
    Formats the page last modification date according to 'html_last_updated_fmt'.
    """
    metadata = app.env.metadata.get(docname, {})
    value = metadata.get("last_updated", None)

    if value and app.config.html_last_updated_fmt:
        try:
            parsed_date = datetime.fromisoformat(value)
            formatted_date = parsed_date.strftime(app.config.html_last_updated_fmt)
            metadata["last_updated"] = formatted_date
        except ValueError:
            del metadata["last_updated"]
            logger.warning(f"{colorize('darkgreen',docname)} has invalid ISO-8601 date: {value}")
    else:
        metadata["last_updated"] = None

def get_title_from_doctree(doctree):
    for node in doctree.traverse(nodes.title):
        return node.astext()
    return None

def generate_breadcrumbs(app, pagename, templatename, context, doctree):
    enriched = []
    base_url = context['theme_base_url'] if 'theme_base_url' in context else None
    if base_url and len(base_url) > 0 and base_url[len(base_url)-1] == '/':
        base_url = base_url[:-1]

    # add the root parent
    if pagename != app.config.master_doc:
        enriched.append({
            'docname': app.config.master_doc,
            'link': f'{len(os.path.dirname(pagename).split('/')) * '../'}index.html',
            'title': context['project'],
            'abs_link': f'{base_url}/index.html' if base_url else None
        })
    # add parents
    for parent in context.get("parents", []):
        link = parent.get('link', '')
        if link.endswith('.html'):
            link = link[:-5]
        docname = normalize_path(os.path.join(os.path.dirname(pagename), link))

        enriched.append({
            **parent,
            "docname": docname or link,
            'abs_link': f'{base_url}/{docname}.html' if base_url else None
        })
    # add current document
    if doctree:
        enriched.append({
            'docname': pagename,
            'link': f'{os.path.basename(pagename)}.html',
            'title': get_title_from_doctree(doctree),
            'abs_link': f'{base_url}/{pagename}.html' if base_url else None
        })
    context["breadcrumbs"] = enriched

def filter_regex_search(value, pattern):
    return bool(re.search(pattern, value))

def _on_builder_inited(app):
        app.builder.templates.environment.filters["regex_search"] = filter_regex_search

def setup(app):
    app.set_translator("html", DesignSystemTranslator)
    setup_extensions(app)
    setup_toc(app)

    # add Sphinx message catalog for translations; it seems Sphinx expects the catalog name to be 'sphinx'
    locale_dir = os.path.join(os.path.dirname(__file__), 'locales')
    app.add_message_catalog('sphinx', locale_dir)
    # register the theme
    theme_path = os.path.abspath(os.path.dirname(__file__))
    app.add_html_theme('sphinx_govbr_theme', theme_path)

    app.connect("builder-inited", _on_builder_inited)
    app.connect("doctree-resolved", _on_doctree_resolved)
    app.connect("html-page-context", generate_breadcrumbs)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }

from .toc import setup as setup_toc
import os
import re
import json
from sphinx.util import logging
from sphinx.util.console import colorize
import time
from datetime import datetime
from .translator import DesignSystemTranslator
from .roles import BrLinkRole
from .extensions.cardlist import setup_extensions
from docutils import nodes
from urllib.parse import urljoin
from pathlib import Path

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

def normalize_sphinx_path(path: str) -> str:
    """
    Normalize a Sphinx-style abstract POSIX path (docname or URI-like),
    resolving '.' and '..' without filesystem access.

    Rules aligned with Sphinx docname semantics:
    - '.' is ignored
    - '..' pops previous segment if possible
    - absolute paths cannot go above root
    - relative paths preserve leading '..' if necessary
    """

    if path is None:
        return ""

    absolute = path.startswith("/")
    parts = path.split("/")

    stack = []

    for part in parts:
        if part == "" or part == ".":
            continue

        if part == "..":
            if stack and stack[-1] != "..":
                # normal backtracking
                stack.pop()
            else:
                # cannot resolve further
                # only allowed to accumulate for relative paths
                if not absolute:
                    stack.append("..")
        else:
            stack.append(part)

    normalized = "/".join(stack)

    if absolute:
        return "/" + normalized if normalized else "/"

    return normalized or "."

def get_title_from_doctree(doctree):
    for node in doctree.traverse(nodes.title):
        return node.astext()
    return None

def add_docname_to_parents(app, pagename, templatename, context, doctree):
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
        docname = normalize_sphinx_path(os.path.join(os.path.dirname(pagename), link))

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

def _make_absolute_url(path, base):
    return urljoin(base, path)

def setup(app):
    app.add_role("br_link", BrLinkRole())
    app.set_translator("html", DesignSystemTranslator)
    setup_extensions(app)
    setup_toc(app)

    # add Sphinx message catalog for translations; it seems Sphinx expects the catalog name to be 'sphinx'
    locale_dir = os.path.join(os.path.dirname(__file__), 'locales')
    app.add_message_catalog('sphinx', locale_dir)
    # register the theme
    theme_path = os.path.abspath(os.path.dirname(__file__))
    app.add_html_theme('sphinx_govbr_theme', theme_path)

    app.connect("doctree-resolved", _on_doctree_resolved)
    app.connect("html-page-context", add_docname_to_parents)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }

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

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }

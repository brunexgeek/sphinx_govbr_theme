from sphinx.environment.adapters.toctree import TocTree
import sphinx.addnodes
from .toc import TreeGenerator, toc_to_dicts
import os
import re
import json
from sphinx.util import logging
from sphinx.util.console import colorize
import time
from datetime import datetime
from typing import Any, Type
from .translator import DesignSystemTranslator
from .roles import BrLinkRole

logger = logging.getLogger(__name__)

GOVBR_HAS_TOC = '_govbr__has_toc'
GOVBR_TOC_PRUNING = 'toc_pruning'

H1_REGEX = re.compile(r'<h1[^>]*>.*?</h1>', flags=re.DOTALL)
mapper = None

class Clock:

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.time()
        logger.info(f'{end} {colorize('blue',self.name)} took {'{:.6f}'.format(end - self.start)} seconds')

def get_config(app, name : str, value : Any, value_type : Type):
    if name in app.config.html_theme_options:
        temp = app.config.html_theme_options[name]
        if not isinstance(temp, value_type):
            raise ApplicationError("Configuration option '{name}' must be a value of type '{valuetype}'")
        return temp
    return value

def remove_first_h1(html):
    match = H1_REGEX.search(html)
    if match:
        removed = match.group(0)
        cleaned = H1_REGEX.sub('', html, count=1)
        return removed, cleaned
    else:
        return "", html

def extract_title(context):
    context['govbr_title'], context['govbr_body'] = remove_first_h1(context.get('body', ''))

def custom_toc_generation(app, pagename, templatename, context, doctree):
    if pagename in ['genindex']:
        return

    #extract_title(context)
    current_url = pagename
    uid = 1

    # compute the TOC tree
    with Clock('toctree.get_toctree_for'):
        toctree = TocTree(app.env)
        raw_toc = toctree.get_toctree_for(pagename, app.builder, False)
        # TODO store the result from the first execution to reuse on other calls

    # generate a custom TOC tree
    with Clock('TreeGenerator'):
        prune = get_config(app, GOVBR_TOC_PRUNING, False, bool)
        gen = TreeGenerator(app.env, pagename, app.config.master_doc, raw_toc, prune)
        context['govbr_toc_map'] = gen.get_global_toc()
        if doctree and not doctree.get(GOVBR_HAS_TOC, False):
            context['govbr_local_toc_map'] = gen.get_local_toc()
        elif app.config.html_theme_options.get('show_child_topics', False):
            logger.warning(f"ignoring local TOC for '{pagename}' because document has visible TOC")
        pageentry = gen.get_pageentry()
        context['govbr_parent'] = pageentry['parent'] if pageentry and 'parent' in pageentry else None
        context['govbr_root'] = gen.get_root()

def custom_template_selection(app, pagename, templatename, context, doctree):
    context['govbr_template'] = templatename
    selected = None

    # check if we should override the template based on 'template_overrides'
    if mapper:
        selected = mapper.select(pagename)
        if selected:
            context['govbr_template'] = selected

    # check if we should override the template based on 'template' metadata
    if context and 'meta' in context and context['meta'] and 'template' in context['meta']:
        name = context['meta']['template'].strip()
        if not name.endswith('.html'):
            raise ApplicationError("Templates must use extension '.html'")
        if name.find('/') >= 0:
            raise ApplicationError("Invalid character in template name")
        context['govbr_template'] = selected = name

    if selected:
        logger.info(f"Changing {colorize('darkgreen', pagename)} template to {colorize('darkgreen', selected)}")
    return selected

def custom_doctree_inspection(app, doctree):
    it = doctree.findall(sphinx.addnodes.toctree)
    doctree[GOVBR_HAS_TOC] = False
    for node in it:
        if 'hidden' in node and not bool(node['hidden']):
            doctree[GOVBR_HAS_TOC] = True
            break

def custom_metadata_processing(app, doctree, docname):
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

    # add Sphinx message catalog for translations; it seems Sphinx expects the catalog name to be 'sphinx'
    locale_dir = os.path.join(os.path.dirname(__file__), 'locales')
    print(locale_dir)
    app.add_message_catalog('sphinx', locale_dir)
    # register the theme
    theme_path = os.path.abspath(os.path.dirname(__file__))
    app.add_html_theme('sphinx_govbr_theme', theme_path)

    app.connect('doctree-read', custom_doctree_inspection)
    app.connect('html-page-context', custom_toc_generation)
    app.connect("doctree-resolved", custom_metadata_processing)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }

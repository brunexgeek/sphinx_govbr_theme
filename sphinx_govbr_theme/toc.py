from typing import Any, Type
import sphinx.addnodes
from sphinx.environment.adapters.toctree import TocTree
from docutils import nodes
from sphinx.addnodes import compact_paragraph, toctree
from sphinx.util import logging
from sphinx.util.console import colorize
import json
import os
import pickle
import time
from pathlib import Path

GOVBR_CACHE_NAME = 'govbr_toc_cache'
GOVBR_HAS_TOC = '_govbr__has_toc'
GOVBR_TOC_PRUNING = 'toc_pruning'

logger = logging.getLogger(__name__)

class Clock:

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.time()
        logger.info(f'{end} {colorize('blue',self.name)} took {'{:.6f}'.format(end - self.start)} seconds')

class TreeGenerator():

    def __init__(self, env, pagename : str, masterdoc : str, node : nodes.Node, prune = False):
        self.env = env
        self.uid = 1
        self.pagename = None
        self.pageentry = None
        self.root = None
        self.prune = prune
        self.global_toc = []
        self.local_toc = []
        self.dirname = os.path.dirname(pagename)
        self.pagename = pagename

        self._compute_global_toc(node)
        self._extract_local_toc(pagename, masterdoc)

    def _parse_list_item(self, node):
        entry = {'is_path' : False}
        for sub in node.children:
            if isinstance(sub, compact_paragraph):
                for item in sub.children:
                    if isinstance(item, nodes.reference):
                        # deduces the entry's pagename
                        clean_uri = item['refuri']
                        if (pos := clean_uri.find('#')) >= 0:
                            clean_uri = clean_uri[:pos]
                        if clean_uri == '':
                            pname = self.pagename
                        else:
                            pname = os.path.normpath(os.path.join(self.dirname, clean_uri))
                        pname = pname[:-5] if pname.endswith('.html') else pname

                        entry = {
                            'title' : item.astext(),
                            'caption': self.env.metadata[pname].get("caption", ""),
                            'url' : '#' if not item['refuri'] else item['refuri'],
                            'is_active' : not item['refuri'],
                            'is_path' : not item['refuri'],
                            'classes' : sub['classes'] if 'classes' in sub else [],
                            'pagename' : pname,
                            'anchor' : None if not item['anchorname'] else item['anchorname'],
                            'id' : self.uid,
                        }
                        self.uid = self.uid + 1

                        # sanity check for active item
                        if entry['is_active'] and not (pname == self.pagename):
                            logger.warning(f'inconsistent active item detection ({self.pagename}, {pname}, {entry['is_active']})')
                        break
            elif isinstance(sub, nodes.bullet_list):
                children, is_path = self._parse_bullet_list(sub)
                if len(children) > 0:
                    # sort children so embedded section (referenced by anchors) are on the top;
                    # we do this because the local TOC is always put in the bottom
                    # of the page, after all embedded sections
                    entry['children'] = sorted(children, key=lambda x: not x['anchor'])
                    # update children with a reference to their parent (current entry)
                    for child in entry['children']:
                        child['parent'] = {'title': entry['title'], 'url': entry['url']}
                    # if any child is a path to the active topic, so do we
                    entry['is_path'] = is_path or entry['is_path']

                    # collect children for the local TOC from every page with the same pagename;
                    # more than one page can have the same pagename in case of multiple headings
                    # and each heading can containg it own toctree declaration
                    if self.pagename == entry['pagename']:
                        for child in entry['children'] :
                            if child['anchor']:
                                continue
                            self.local_toc.append({
                                'title' : child['title'],
                                'url' : child['url'],
                            })
                        #logger.warning(f'--- self.pagename is {colorize('darkgreen', self.pagename)} and current pagename is {colorize('darkgreen', entry['pagename'])}:\n{self.local_toc}')

        if 'title' not in entry or not entry['title']:
            return None
        # set reference to local TOC
        if entry['is_active']:
            self.pageentry = entry
        return entry, (entry['is_path'] if 'is_path' in entry else False)

    def _parse_bullet_list(self, node):
        result = []
        is_path = False
        for item in node.children:
            if isinstance(item, nodes.list_item):
                res1, res2 = self._parse_list_item(item)
                if res1 != None:
                    result.append(res1)
                is_path = is_path or res2
        return result, is_path

    def _compute_global_toc(self, node):
        if node == None:
            return

        # the first level is a paragraph with one or more 'bullet_list' nodes, each of them
        # optionally preceeded by a 'title' node (if the toctree has a caption)
        title = ""
        for child in node.children:
            if isinstance(child, nodes.title):
                title = child.astext()
            elif isinstance(child, nodes.bullet_list):
                children, is_path = self._parse_bullet_list(child)
                group = {
                    'caption': title,
                    'children': children,
                    'is_path': is_path
                }
                self.global_toc.append(group)
                title = ""

        if self.prune and len(self.global_toc) == 1:
            while len(self.global_toc[0]['children']) == 1:
                self.root = {
                    'title': self.global_toc[0]['children'][0]['title'],
                    'url': self.global_toc[0]['children'][0]['url']
                }
                self.global_toc[0]['children'] = self.global_toc[0]['children'][0]['children']

    def _extract_local_toc(self, pagename : str, masterdoc : str):
        if not self.global_toc:
            return

        if pagename == masterdoc:
            self.local_toc = []
            # since 'masterdoc' has no entry in the TOC, 'self.local_toc' will be empty;
            # so we create a local TOC using children from the top entries of the TOC
            # which are just caption entries and point to no real content
            for item in self.global_toc:
                for child in item['children']:
                    if 'anchor' in child and child['anchor']:
                        continue
                    entry = {
                        'title': child['title'],
                        'url': child['url']
                    }
                    self.local_toc.append(entry)

    def get_global_toc(self):
        return self.global_toc

    def get_local_toc(self):
        return self.local_toc

    def get_pageentry(self):
        return self.pageentry

    def get_root(self):
        return self.root


def get_config(app, name : str, value : Any, value_type : Type):
    if name in app.config.html_theme_options:
        temp = app.config.html_theme_options[name]
        if not isinstance(temp, value_type):
            raise ApplicationError("Configuration option '{name}' must be a value of type '{valuetype}'")
        return temp
    return value

def _on_html_page_context(app, pagename, templatename, context, doctree):
    if pagename in ['genindex']:
        return

    # if the page is up to date and its TOC is cached, skip TOC generation
    cache = app.govbr_toc_cache
    outdated = set(app.builder.get_outdated_docs())
    if cache and pagename not in outdated and pagename in cache:
        computed = cache.get(pagename)
        context['govbr_toc_map'] = computed['govbr_toc_map']
        context['govbr_local_toc_map'] = computed['govbr_local_toc_map']
        context['govbr_parent'] = computed['govbr_parent']
        context['govbr_root'] = computed['govbr_root']
        logger.info(f"retrieved '{pagename}' TOC information from cache")
        return

    # compute the TOC tree
    with Clock('toctree.get_toctree_for'):
        toctree = TocTree(app.env)
        raw_toc = toctree.get_toctree_for(pagename, app.builder, False)
        # TODO store the result from the first execution to reuse on other calls

    # generate a custom TOC tree
    with Clock('TreeGenerator'):
        prune = get_config(app, GOVBR_TOC_PRUNING, False, bool)
        gen = TreeGenerator(app.env, pagename, app.config.master_doc, raw_toc, prune)
        govbr_toc_map = gen.get_global_toc()
        if doctree and not doctree.get(GOVBR_HAS_TOC, False):
            govbr_local_toc_map = gen.get_local_toc()
        elif app.config.html_theme_options.get('show_child_topics', False):
            logger.warning(f"ignoring local TOC for '{pagename}' because document has visible TOC")
            govbr_local_toc_map = None
        pageentry = gen.get_pageentry()
        govbr_parent = pageentry['parent'] if pageentry and 'parent' in pageentry else None
        govbr_root = gen.get_root()

        computed = {
            'govbr_toc_map': govbr_toc_map,
            'govbr_local_toc_map': govbr_local_toc_map,
            'govbr_parent': govbr_parent,
            'govbr_root': govbr_root,
        }
        cache[pagename] = computed
        for key in computed:
            context[key] = computed[key]


def _on_doctree_read(app, doctree):
    """
    Check whether the doctree contains a visible TOC.
    """
    it = doctree.findall(sphinx.addnodes.toctree)
    doctree[GOVBR_HAS_TOC] = False
    for node in it:
        if 'hidden' in node and not bool(node['hidden']):
            doctree[GOVBR_HAS_TOC] = True
            break

def _on_builder_inited(app):
    """
    Load the TOC cache.
    """
    app.govbr_toc_cache = load_toc_cache(app)

def _on_build_finished(app, exception):
    """
    Persist the TOC cache.
    """
    if exception is not None:
        return

    save_toc_cache(app, app.govbr_toc_cache)

def _on_purge_doc(app, env, docname):
    if hasattr(env, 'govbr_toc_cache'):
        app.govbr_toc_cache.pop(docname, None)

def get_toc_cache_path(app):
    return Path(app.doctreedir) / 'govbr_toc_cache.pickle'

def load_toc_cache(app):
    path = get_toc_cache_path(app)
    if not path.exists():
        return {}
    try:
        with path.open("rb") as f:
            return pickle.load(f)
    except Exception as exc:
        app.warn(f"Failed to load TOC cache: {exc}")
        return {}

def save_toc_cache(app, cache):
    path = get_toc_cache_path(app)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")

    try:
        with tmp_path.open("wb") as f:
            pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)

        tmp_path.replace(path)

    except Exception as exc:
        app.warn(f"Failed to save cache: {exc}")

def setup(app):
    app.connect("builder-inited", _on_builder_inited)
    app.connect("build-finished", _on_build_finished)
    app.connect('html-page-context', _on_html_page_context)
    app.connect("env-purge-doc", _on_purge_doc)
    app.connect('doctree-read', _on_doctree_read)

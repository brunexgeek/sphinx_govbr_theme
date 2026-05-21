from docutils import nodes
from sphinx.addnodes import compact_paragraph, toctree
import json
import os
from sphinx.util import logging
from sphinx.util.console import colorize

logger = logging.getLogger(__name__)

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


    def prune(prefix : str):
        pass

    def get_global_toc(self):
        return self.global_toc

    def get_local_toc(self):
        return self.local_toc

    def get_pageentry(self):
        return self.pageentry

    def get_root(self):
        return self.root


def toc_to_dicts(toctree_node):
    """
    Convert a Sphinx toctree node into a hierarchy of Python dicts.

    Returns:
        list of dicts:
        {
            "title": str,
            "url": str,
            "children": [...]
        }
    """

    def extract_ref(refnode):
        """Extract title + URL from a reference node."""
        title = refnode.astext()

        # Sphinx stores internal links as refuri or anchor-like targets
        url = refnode.get("refuri")

        # fallback for internal documents
        #if not url:
        #    docname = refnode.get("reftarget")
        #    if docname:
        #        url = builder.get_relative_uri("", docname)

        return title, url or "#"

    def walk(node):
        items = []

        for child in node:
            # Each entry is usually a list_item
            if isinstance(child, nodes.list_item):
                entry = {
                    "title": None,
                    "url": None,
                    "children": []
                }

                for sub in child:

                    if isinstance(sub, compact_paragraph) and len(sub.children) == 1:
                        sub = sub.children[0]
                        if isinstance(sub, nodes.reference):
                            title, url = extract_ref(sub)
                            entry["title"] = title
                            entry["url"] = url

                    # Nested TOC (sub-toctree)
                    elif isinstance(sub, nodes.bullet_list):
                        entry["children"] = walk(sub)

                if entry["title"] is not None:
                    items.append(entry)

        return items

    # TOC root is usually a bullet_list or container
    if isinstance(toctree_node, nodes.bullet_list):
        return walk(toctree_node)

    # fallback: search inside
    #bullet_lists = toctree_node.traverse(nodes.bullet_list)
    #if bullet_lists:
    #    return walk(bullet_lists[0])

    return []
import json
import os
from sphinx.util.osutil import copyfile as sphinx_copyfile
from sphinx.errors import SphinxError
from pathlib import Path
from docutils import nodes
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset_file
from sphinx.util import logging

logger = logging.getLogger(__name__)

class cardlist(nodes.General, nodes.Element):
    pass

class BrCardListDirective(SphinxDirective):
    has_content = True

    def run(self):
        raw_content = "\n".join(self.content)

        try:
            items = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise self.error(f"Invalid JSON: {exc}")

        if not isinstance(items, list):
            raise self.error("Content must be a JSON array")

        filtered = []

        for item in items:
            if not isinstance(item, dict):
                raise self.error("Each item must be an object")

            if 'xref' in item:
                current = {'xref': item['xref']}
            else:
                required = ["title", "url", "description"]
                for field in required:
                    if field not in item:
                        raise self.error(
                            f"Missing required field: {field}"
                        )
                current = {}
                for name in required:
                    current[name] = item[name]
                if 'image' in item:
                    current['image'] = item['image']

            filtered.append(current)

        node = cardlist()
        node["items"] = filtered

        for item in items:
            if 'xref' in item:
                ref = addnodes.pending_xref(
                    '',
                    refdomain='std',
                    reftype='ref',
                    reftarget=item['xref'],
                    modname=None,
                    classname=None,
                    refExplicit=False,
                )
                ref += nodes.Text("")
                node += ref
            else:
                node += nodes.Element()

        return [node]

def visit_cardlist_html(self, node):
    env = self.builder.templates.environment
    fn_escape = env.filters["escape"]
    fn_striptags = env.filters["striptags"]

    self.body.append('<div class="br_cardlist"><div class="row">')

    i = 0
    for item in node["items"]:
        if 'xref' in item:
            if not isinstance(node[i] , nodes.reference):
                logger.warn(f"Unresolved reference '{item['xref']}'; skipping card")
                continue

            # infers the docname
            docname = node[i].get('refuri', '')
            if '#' in docname:
                docname = docname.split('#')[0]
            if docname.endswith('.html'):
                docname = docname[:-5]
            # retrieve meta fields
            frontmatter = self.builder.env.metadata.get(docname, {})

            title = node[i][0].astext()
            href = node[i]['refuri']
            image = frontmatter.get('card_image', None)
            description = frontmatter.get('description', '')

            # make the image path relative to the current document
            if image:
                image = (Path(self.builder.srcdir) / Path(docname).parent / image).resolve()
                if image.is_relative_to(Path(self.builder.srcdir)):
                    image = image.relative_to(Path(self.builder.srcdir))
                else:
                    image = None
        else:
            title = fn_escape(fn_striptags(item['title']))
            href = fn_escape(fn_striptags(item['url']))
            image = fn_escape(fn_striptags(item['image']))
            description = fn_escape(fn_striptags(item['description']))
        i += 1

        if image:
            # build the input and output paths, ensuring they do not escape the allowed directories
            outroot = Path(self.builder.outdir) / '_static' / 'cards'
            image_source = (Path(self.builder.srcdir) / Path(self.builder.env.docname).parent / image).resolve()
            image_dest = (outroot / Path(self.builder.env.docname).parent / image).resolve()
            if image_source.is_relative_to(Path(self.builder.srcdir)) and image_source.exists() and image_dest.is_relative_to(outroot):
                os.makedirs(image_dest.parent, exist_ok=True)
                sphinx_copyfile(image_source, image_dest)
                image = image_dest.relative_to(Path(self.builder.outdir))
            else:
                image = None

        self.body.append(
            f"""
                <div class="col-md-4">
                    <a class="br-card d-flex flex-column flex-fill hover" href="{href}">
                        <div class="card-header">
                            <p class="text-up-02 text-weight-bold my-0">{title}</p>
                        </div>
                        <div class="card-content">
            """
        )

        if image:
            self.body.append(
                f"""
                                <div class="card-img d-flex justify-content-center align-itens-center">
                                    <img src="{image}" class="img-fluid" alt="Cores">
                                </div>
                """
            )
        self.body.append(
            f"""
                            <div>
                                <p>{description}</p>
                            </div>
                        </div>
                    </a>
                </div>
            """
        )

    # skip children (references)
    raise nodes.SkipChildren

def depart_cardlist_html(self, node):
    self.body.append("</div></div>")

def setup_cardlist(app):
    app.add_node(cardlist, html=(visit_cardlist_html, depart_cardlist_html))
    app.add_directive("br_cardlist", BrCardListDirective)

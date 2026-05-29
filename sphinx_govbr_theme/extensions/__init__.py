from .cardlist import BrCardListDirective, cardlist, visit_cardlist_html, depart_cardlist_html
from .roles import BrLinkRole

def setup(app):
    app.add_node(cardlist, html=(visit_cardlist_html, depart_cardlist_html))
    app.add_directive("br_cardlist", BrCardListDirective)
    app.add_role("br_link", BrLinkRole())
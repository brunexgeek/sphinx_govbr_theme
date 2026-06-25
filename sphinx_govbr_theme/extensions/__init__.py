from .cardlist import setup_cardlist
from .detail import setup_detail
from .roles import BrLinkRole, br_open_accordion, br_close_accordion

def setup(app):
    app.add_role("br_link", BrLinkRole())
    app.add_role("br_open_accordion", br_open_accordion)
    app.add_role("br_close_accordion", br_close_accordion)
    setup_cardlist(app)
    setup_detail(app)
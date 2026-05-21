FROM sphinxdoc/sphinx:8.2.3

RUN apt update && apt install -y gettext && apt clean && \
    pip install polib sphinx-autobuild myst-parser

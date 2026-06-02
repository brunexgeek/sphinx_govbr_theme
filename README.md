# sphinx_govbr_theme

Tema Sphinx baseado no [Design System do gov.br](https://www.gov.br/ds/home).

![Theme screenshot](example/screenshot.webp)

## Opções do tema

O tema oferece suporte às seguintes opções, que podem ser usadas na variável `html_theme_options` do seu `conf.py`.

### show_child_topics

Se `True`, uma lista de tópicos filhos será exibida após o conteúdo do documento em cada página que não tenha um `toctree` visível (ou seja, incluindo `:hidden:`). O valor padrão é `False`.

### show_parent_topic

Se `True`, um link para o tópico pai será exibido após o conteúdo do documento. O valor padrão é `False`.

### header_extra_links

Lista de entradas a serem exibidas no topo da página. Útil para disponibilizar links externos, cujo conteúdo é relacionado. Cada entrada é um `dict` com os seguintes campos:

* `title`: texto usado como rótulo da entrada do menu;
* `url`: URL de destino.

Links extras usam o alvo `_blank`, portanto serão abertos em outra aba/janela.

```python
'header_extra_links': [
    {
        'title': 'Astronomia na Wikipédia',
        'url': 'https://en.wikipedia.org/wiki/Astronomy'
    },
    {
        'title': 'Site da NASA',
        'url': 'https://www.nasa.gov/'
    }
]
```

### project_subtitle

Define o texto que aparece logo abaixo do título do site, na barra superior.

```python
project_subtitle = "Design System | Versão 3.7.0"
```

### theme_enable_discussion

Habilita a aba de discussão em cada página da documentação. O valor padrão é `false`.

## Componentes

Os seguintes componentes estão disponíveis para uso nos documentos:

Componente | Descrição
-----------|---------------
[br_cardlist](docs/br_cardlist.md)    | *Container* com uma lista de *cards*.

## Metadados

Os campos abaixo pode ser inseridos como [campos de metadados](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#file-wide-metadata) num documento RST ou no [frontmatter](https://mystmd.org/guide/configuration) de um documento Markdown (MyST).

Campo|Descrição
-----|-----------
`:description:`|Descrição curta do conteúdo, injetado como uma tag `meta` no HTML gerado. Esta descrição também é utilizada em *cards*.
`:last_updated:`|Data da última atualização do documento. Se omitida, será usada a data em que o HTML foi gerado.
`:show_child_topics:`|Igual à opção de configuração `show_child_topics`, mas específica para uma página.

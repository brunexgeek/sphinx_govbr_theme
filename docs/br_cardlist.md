# br_cardlist

A diretiva `br_cardlist` permite criar listas de *cards* na saída HTML da documentação.

Cada *card* pode referenciar outra página da documentação usando `xref` ou definir manualmente um título, descrição, imagem e URL.

Exemplo em reStructuredText:
```rst
.. br_cardlist::

   [
     {
       "xref": "getting-started"
     },
     {
       "title": "Exemplo",
       "url": "url/para/conteudo/interno/ou/externo",
       "image": "_static/img/start.png",
       "description": "Descrição do card."
     }
   ]
```

Exemplo em Markdown (MyST):
````markdown
```{br_cardlist}
   [
     {
       "xref": "getting-started"
     },
     {
       "title": "Exemplo",
       "url": "url/para/conteudo/interno/ou/externo",
       "image": "_static/img/start.png",
       "description": "Descrição do card."
     }
   ]
```
````

Quando apenas `xref` é informado, a extensão tenta obter automaticamente:

* título da página
* descrição definida pelo campo `:description:`
* imagem definida pelo campo `:card_image:`

## Estrutura do objeto

Cada item do array JSON representa um *card*. Os campos suportados são:

Campo         | Tipo   | Descrição
------------- | ------ | ---------------
`xref`        | string | Referência para uma página da documentação.
`title`       | string | Título do *card*.
`url`         | string | URL de destino do *card*.
`image`       | string | Caminho ou URL da imagem. Se omitido, nenhuma imagem é usada no *card*.
`description` | string | Texto descritivo.

## Regras de resolução

Quando `xref` é informado, o *card* aponta para a página referenciada. Neste caso o `title`, `description` e `image` são preenchidos automaticamente a partir do conteúdo da página. Note que o campo `image` será preenchido com o valor do metadado `:card_image:` do documento. Nenhum outro valor do objeto JSON além de `xref` é usado.

Quando o `xref` não é informado, os campos `title`, `description` e `url` devem estar presentes no objeto JSON. O campo `image` é opcional.

O campo `image` admite caminhos relativos ao `_static` e URLs absolutas, porém valores oriundos do metadado `:card_image:` sempre precisam ser relativos ao `_static`.

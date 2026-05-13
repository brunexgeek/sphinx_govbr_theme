# Sphinx/Jinja translation instructions

This guide provides step-by-step instructions for creating or updating translations of theme-specific terms.

Keep in mind that Sphinx comes with a built-in set of translations for many common interface terms. Whenever possible, it's recommended to use the translations already provided by Sphinx to ensure consistency and reduce duplication. You can find the official `.pot` file in the [Sphinx GitHub repository](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/locale/sphinx.pot).


1. Make sure all translatable strings are marked in the template files.

    ```jinja
    {{ _('This is translatable') }}
    {% trans %}This is translatable too{% endtrans %}
    ```

2. Use `xgettext` to scan files and generate a `.pot` file. Make sure to name the output file `sphinx.pot`, otherwise the translations will not work in the theme.

    ```bash
    xgettext --from-code=UTF-8 --language=Python --keyword=_ -o sphinx.pot ../*.html
    ```

3. Create a `.po` file from the `.pot`. Be aware that the output file will be overwritten and its contents will be lost; you can use `msgmerge` to keep existing translations.

    ```bash
    mkdir -p pt_BR/LC_MESSAGES && \
    msginit --no-translator -i sphinx.pot --locale=pt_BR.UTF-8 -o pt_BR/LC_MESSAGES/sphinx.po --locale=pt_BR
    ```

    This example creates a Portuguese translation file with placeholders for each string.

4. Edit the `.po` and fill in the `msgstr` fields.

    ```po
    msgid "Hello, world!"
    msgstr "Olá, mundo!"
    ```

    Make sure your using the correct text encoding in the `Content-Type` attribute; the default value is `ASCII`.

    ```
    "Content-Type: text/plain; charset=UTF-8\n"
    ```

5. Compile the `.po` into a `.mo` file.

    ```bash
    msgfmt pt_BR/LC_MESSAGES/sphinx.po -o pt_BR/LC_MESSAGES/sphinx.mo
    ```

    This binary `.mo` file is used at runtime by Sphinx/Jinja.






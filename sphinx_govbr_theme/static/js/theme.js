let toc_root = null;

function update_active(scroll) {
    if (toc_root == null) {
        if ((toc_root = document.querySelector('.cc-toc-nav')) == null)
            return;
    }

    // get the current anchor
    let hash = window.location.hash;
    if (hash.length == 0)
        hash = '#';
    // removes the attribute to every hyperlink
    toc_root.querySelectorAll('.cc-toc-nav a[aria-current=true]').forEach(element => {
        element.removeAttribute('aria-current');
    });
    // set the attribute in the correct element
    let element = toc_root.querySelector(`.cc-toc-nav a[href='${hash}'`);
    if (element) {
        element.setAttribute('aria-current', 'true');
        if (scroll)
            element.scrollIntoView({block: "center"});
    }
}

document.addEventListener("DOMContentLoaded", function(event){
    // ensure external hyperlinks will open on a new tab/window
    document.querySelectorAll('.rst-content a.external').forEach(link => {
        link.setAttribute('target', '_blank');
    });
    // set event listeners to all 'expand' hyperlinks
    document.querySelectorAll('div.cc-expand-icon.icon-down').forEach(element => {
        element.addEventListener('click', event => {
            const id = event.currentTarget.getAttribute('data-id', null);
            if (id != null) {
                document.querySelector('#cc-toc-children-' + id).style.display = "block";
                document.querySelector('#cc-expand-' + id).style.display = "none";
                document.querySelector('#cc-collapse-' + id).style.display = "block";
            }
        })
    });
    // set event listeners to all 'collapse' hyperlinks
    document.querySelectorAll('div.cc-expand-icon.icon-up').forEach(element => {
        element.addEventListener('click', event => {
            const id = event.currentTarget.getAttribute('data-id', null);
            if (id != null) {
                document.querySelector('#cc-toc-children-' + id).style.display = "none";
                document.querySelector('#cc-expand-' + id).style.display = "block";
                document.querySelector('#cc-collapse-' + id).style.display = "none";
            }
        })
    });
    // set event listeners to all header menu items
    document.querySelectorAll('#cc-menu-bar .bx--header__menu-title').forEach(element => {
        element.addEventListener('click', event => {
            const expanded = event.currentTarget.getAttribute('aria-expanded') === 'true';
            event.currentTarget.setAttribute('aria-expanded', !expanded);
        });
    });
    // set event listeners to all paging buttons (blog index)
    document.querySelectorAll('#blog .navigation input').forEach(element => {
        element.addEventListener('click', event => {
            // adjust button selection
            document.querySelectorAll('#blog .navigation input').forEach(element => {
                element.classList.remove('selected');
            });

            // select the correct page
            const page = event.currentTarget.getAttribute('data-page', 1);
            document.querySelectorAll('#blog .blogposts .page').forEach(element => {
                const current = element.getAttribute('data-page');
                if (current && current == page)
                    element.style.display = 'block';
                else
                    element.style.display = 'none';
            });
            event.currentTarget.classList.add('selected');
        });
    });
    // select the TOC item for the current page; this is only necessary for URLs with anchor
    update_active(true);
});

window.addEventListener("hashchange", () => {
  update_active();
});


function update_active(menuId, scroll) {
    const toc_root = document.querySelector(menuId);
    if (toc_root) {
        // get the current anchor
        let hash = window.location.hash;
        if (hash.length == 0)
            hash = '#';
        // set the attribute in the correct element
        let elements = toc_root.querySelectorAll(`li a[href='${hash}'`);
        if (elements && elements.length > 0) {
            // removes the attribute to every hyperlink
            toc_root.querySelectorAll('li.active').forEach(element => {
                element.classList.remove('active');
            });
        }
        elements.forEach(element => {
            element = element.closest('li');
            element.classList.add('active');
            if (scroll)
                element.scrollIntoView({block: "center"});
        });
    }
}

document.addEventListener("DOMContentLoaded", function(event){
    // ensure external hyperlinks will open on a new tab/window
    document.querySelectorAll('.rst-content a.external').forEach(link => {
        link.setAttribute('target', '_blank');
    });
    // set event listeners open submenus
    document.querySelectorAll('button.br-button.arrow').forEach(element => {
        element.addEventListener('click', event => {
            const id = event.currentTarget.getAttribute('data-id', null);
            const expanded = event.currentTarget.getAttribute('aria-expanded', 'false') === 'true';
            if (id != null) {
                let submenu = document.querySelector('#submenu-' + id)
                if (submenu) {
                    submenu.style.display = (expanded) ? 'none' : 'block';
                    //submenu.classList.value = (expanded) ? 'off' : 'on';
                    event.currentTarget.setAttribute('aria-expanded', expanded ? 'false' : 'true');
                }
            }
        })
    });
    // set event listeners to close submenus
    document.querySelectorAll('button.backButton').forEach(element => {
        element.addEventListener('click', event => {
            const id = event.currentTarget.getAttribute('data-id', null);
            if (id != null) {
                let submenu = document.querySelector('#submenu-' + id)
                if (submenu) {
                    submenu.style.visibility = 'hidden';
                    submenu.classList.value = 'off';
                    submenu.setAttribute('aria-hidden', 'true');
                    document.querySelector('#expand-' + id)?.setAttribute('aria-expanded', 'false');
                }
            }
        })
    });
    document.querySelector('#show-navigation')?.addEventListener("click", () => {
        document.getElementById('menu-overlay').removeAttribute('hidden');
        document.getElementById('menu-navigation').removeAttribute('hidden');
    });
    document.querySelectorAll('[data-dismiss="menu"]').forEach(btn =>
        btn.addEventListener('click',() => {
            document.getElementById('menu-overlay').setAttribute('hidden', '');
            document.getElementById('menu-navigation').setAttribute('hidden', '');
        })
    );
    window.addEventListener("hashchange", () => {
        update_active('#menu-navigation');
        update_active('#sidebar-navigation');
    });
    // select the TOC item for the current page; this is only necessary for URLs with anchor
    update_active('#menu-navigation', true);
    update_active('#sidebar-navigation', true);
    console.debug('Done!');
});






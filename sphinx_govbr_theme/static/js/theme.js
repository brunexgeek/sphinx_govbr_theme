let toc_root = null;
let page_header = null;

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
    // set event listeners open submenus
    document.querySelectorAll('button.br-button.arrow').forEach(element => {
        element.addEventListener('click', event => {
            const id = event.currentTarget.getAttribute('data-id', null);
            if (id != null) {
                let submenu = document.querySelector('#submenu-' + id)
                if (submenu) {
                    submenu.style.visibility = 'visible';
                    submenu.classList.value = 'on';
                    submenu.setAttribute('aria-hidden', 'false');
                    event.currentTarget.setAttribute('aria-expanded', 'true');
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

    /*page_header = document.querySelector('header');
        window.onscroll = () => {
        if (page_header && window.pageYOffset > page_header.offsetHeight) {
            if (!page_header.classList.contains('sticky'))
                page_header.classList.add('sticky', 'compact')
        } else {
            if (page_header.classList.contains('sticky'))
                page_header.classList.remove('sticky', 'compact')
        }
    }*/

    document.querySelector('#show-navigation')?.addEventListener("click", () => {
        document.getElementById('menu-overlay').removeAttribute('hidden');
        document.getElementById('menu-navigation').removeAttribute('hidden');
    });

    document.querySelectorAll('button[data-dismiss="menu"]').forEach(btn =>
        btn.addEventListener('click',() => {
            document.getElementById('menu-overlay').setAttribute('hidden', '');
            document.getElementById('menu-navigation').setAttribute('hidden', '');
        })
    );

    // select the TOC item for the current page; this is only necessary for URLs with anchor
    //update_active(true);
    console.info('Done!');
});

window.addEventListener("hashchange", () => {
  update_active();
});




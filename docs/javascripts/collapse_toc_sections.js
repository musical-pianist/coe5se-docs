// Gives each section of the page's table of contents, on the right, an arrow that opens or closes it. Sections start
// open, nothing moves by itself, and the browser remembers each reader's clicks, per page. A page with no sections
// stays as it is.
(function () {
  const toc = document.querySelector(".md-sidebar--secondary .md-nav--secondary > .md-nav__list");
  if (!toc) return;
  const STORAGE_KEY = `coe5se-toc:${location.pathname}`;

  function readChoices() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
      return {};   // A browser with storage turned off, or a value it can't read: the starting states.
    }
  }

  function saveChoices(choices) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(choices));
    } catch {
      // A browser with storage turned off: the click still works, until the page reloads.
    }
  }

  function setOpen(section, open) {
    section.classList.toggle("toc-section--open", open);
    section.querySelector(":scope > .toc-section-toggle").setAttribute("aria-expanded", String(open));
  }

  const choices = readChoices();
  Array.from(toc.children).filter((item) => item.querySelector(":scope > .md-nav")).forEach((section) => {
    const link = section.querySelector(":scope > .md-nav__link");
    const anchor = link.hash.slice(1);
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "toc-section-toggle";
    toggle.setAttribute("aria-label", `Open or close ${link.textContent.trim()}`);
    section.classList.add("toc-section");
    section.insertBefore(toggle, section.querySelector(":scope > .md-nav"));
    setOpen(section, anchor in choices ? choices[anchor] : true);
    toggle.addEventListener("click", () => {
      const open = !section.classList.contains("toc-section--open");
      setOpen(section, open);
      choices[anchor] = open;
      saveChoices(choices);
    });
  });
})();

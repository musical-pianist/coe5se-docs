// The mod explorer on Getting Started: one mod in each of its layouts (.mod-explorer__layout), the layout's files on
// the left (.mod-explorer__files), and the file the reader clicks open on the right (.mod-explorer__pane, matched to its
// button by data-file), so its code keeps the site's colours and annotations. Every caption, file list and pane sits in
// the same grid cell as its kind and only the open one is visible; the panes have a fixed height that a long file
// scrolls inside (site.css), so the box never jumps. Without this script everything shows, one under the other.
document.addEventListener("DOMContentLoaded", () => {
  for (const explorer of document.querySelectorAll(".mod-explorer")) {
    const layouts = [...explorer.querySelectorAll(".mod-explorer__layout")];
    const lists = [...explorer.querySelectorAll(".mod-explorer__files")];
    const panes = [...explorer.querySelectorAll(".mod-explorer__pane")];
    if (!layouts.length || !lists.length) continue;
    const openFile = (list, name) => {
      for (const button of list.querySelectorAll(".mod-explorer__file")) {
        button.setAttribute("aria-selected", String(button.dataset.file === name));
      }
      for (const pane of panes) pane.classList.toggle("mod-explorer__open", pane.dataset.file === name);
    };
    const openLayout = (layout) => {
      for (const button of layouts) button.setAttribute("aria-selected", String(button.dataset.layout === layout));
      for (const el of explorer.querySelectorAll(".mod-explorer__caption, .mod-explorer__files")) {
        el.classList.toggle("mod-explorer__open", el.dataset.layout === layout);
      }
      const list = lists.find((l) => l.dataset.layout === layout);
      openFile(list, list.querySelector(".mod-explorer__file").dataset.file);
    };
    for (const list of lists) {
      for (const button of list.querySelectorAll(".mod-explorer__file")) {
        button.addEventListener("click", () => openFile(list, button.dataset.file));
      }
    }
    for (const button of layouts) button.addEventListener("click", () => openLayout(button.dataset.layout));
    explorer.classList.add("mod-explorer--ready");
    openLayout(layouts[0].dataset.layout);
  }
});

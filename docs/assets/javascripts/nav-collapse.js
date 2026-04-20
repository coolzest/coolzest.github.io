// Make the primary navigation behave like a collapsed folder tree.

(function () {
  function containsActivePage(item) {
    return Boolean(
      item.matches(".md-nav__item--active") ||
        item.querySelector(":scope > .md-nav .md-nav__item--active, :scope > .md-nav .md-nav__link--active")
    );
  }

  function shouldOpenOnLoad(item) {
    return containsActivePage(item);
  }

  function setFolderState(item, expanded) {
    const checkbox = item.querySelector(":scope > input.md-nav__toggle");
    if (!checkbox) {
      return;
    }

    checkbox.checked = expanded;

    const childNav = item.querySelector(":scope > .md-nav");
    if (childNav) {
      childNav.setAttribute("aria-expanded", String(expanded));
    }
  }

  function toggleFolder(item) {
    const checkbox = item.querySelector(":scope > input.md-nav__toggle");
    if (!checkbox) {
      return;
    }

    setFolderState(item, !checkbox.checked);
  }

  function initFolderNav() {
    const nav = document.querySelector(".md-sidebar--primary");
    if (!nav) {
      return;
    }

    nav.querySelectorAll(".md-nav__item--nested").forEach((item) => {
      const checkbox = item.querySelector(":scope > input.md-nav__toggle");
      if (!checkbox) {
        return;
      }

      if (!item.dataset.folderToggleInitialized) {
        item.dataset.folderToggleInitialized = "true";
        setFolderState(item, shouldOpenOnLoad(item));
      }

      if (!checkbox.dataset.folderToggleBound) {
        checkbox.dataset.folderToggleBound = "true";
        checkbox.addEventListener("change", () => {
          setFolderState(item, checkbox.checked);
        });
      }

      const indexLink = item.querySelector(":scope > .md-nav__container > a.md-nav__link");
      if (indexLink && !indexLink.dataset.folderToggleBound) {
        indexLink.dataset.folderToggleBound = "true";
        indexLink.setAttribute("role", "button");
        indexLink.addEventListener("click", (event) => {
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) {
            return;
          }

          event.preventDefault();
          toggleFolder(item);
        });
      }
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initFolderNav);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFolderNav);
  } else {
    initFolderNav();
  }
})();

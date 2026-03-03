// Auto-collapse primary nav, keep active path expanded

document.addEventListener("DOMContentLoaded", () => {
  const nav = document.querySelector(".md-sidebar--primary");
  if (!nav) return;

  nav.querySelectorAll(".md-nav__item--nested").forEach((item) => {
    const checkbox = item.querySelector("input.md-nav__toggle");
    if (checkbox) checkbox.checked = false;
  });

  nav.querySelectorAll(".md-nav__item--active").forEach((active) => {
    let cur = active;
    while (cur && cur !== nav) {
      if (cur.classList && cur.classList.contains("md-nav__item--nested")) {
        const checkbox = cur.querySelector("input.md-nav__toggle");
        if (checkbox) checkbox.checked = true;
      }
      cur = cur.parentElement;
    }
  });
});

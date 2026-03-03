// Lightweight and safe UI helpers (avoid overriding Material navigation state)
const throttle = (fn, delay = 100) => {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= delay) {
      last = now;
      fn(...args);
    }
  };
};

// Header shadow on scroll
const syncHeaderShadow = () => {
  const header = document.querySelector(".md-header");
  if (!header) return;
  if (window.scrollY > 50) header.classList.add("md-header--shadow");
  else header.classList.remove("md-header--shadow");
};

document.addEventListener("DOMContentLoaded", () => {
  window.addEventListener("scroll", throttle(syncHeaderShadow), { passive: true });
  syncHeaderShadow();

  // Keep anchor jumps comfortable, but do not hijack page navigation links.
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      const href = anchor.getAttribute("href");
      if (!href || href === "#" || href.startsWith("#/")) return;
      const target = document.querySelector(href);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
});

(function () {
  function clean(value, fallback) {
    var text = (value || "").trim();
    return text || fallback;
  }

  function codeText(code) {
    function walk(node) {
      if (node.nodeType === Node.TEXT_NODE) return node.textContent;
      if (node.nodeType !== Node.ELEMENT_NODE) return "";
      if (node.matches("[data-code-blank]")) {
        return clean(node.textContent, node.dataset.default || "");
      }

      return Array.from(node.childNodes)
        .map(walk)
        .join("");
    }

    return walk(code).replace(/\n{3,}/g, "\n\n").trim();
  }

  function initCodeBlanks(code) {
    code.querySelectorAll("[data-code-blank]").forEach(function (token) {
      token.addEventListener("focus", function () {
        if (token.textContent.trim() === token.dataset.default) {
          var range = document.createRange();
          range.selectNodeContents(token);
          var selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }
      });
    });
  }

  function codePlaceholderFragment(text) {
    var fragment = document.createDocumentFragment();
    var pattern = /\{\{([^{}]+)\}\}/g;
    var cursor = 0;
    var match;

    while ((match = pattern.exec(text)) !== null) {
      fragment.appendChild(document.createTextNode(text.slice(cursor, match.index)));

      var hint = match[1].trim();
      var token = document.createElement("span");
      token.setAttribute("data-code-blank", "");
      token.setAttribute("contenteditable", "true");
      token.setAttribute("spellcheck", "false");
      token.setAttribute("role", "textbox");
      token.setAttribute("aria-label", hint);
      token.dataset.default = hint;
      token.textContent = hint;
      fragment.appendChild(token);

      cursor = pattern.lastIndex;
    }

    fragment.appendChild(document.createTextNode(text.slice(cursor)));
    return fragment;
  }

  function replacePlaceholdersInCode(code) {
    var walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    var textNodes = [];
    var node;

    while ((node = walker.nextNode())) {
      if (node.parentElement && node.parentElement.closest("[data-code-blank]")) continue;
      if (node.textContent.match(/\{\{[^{}]+\}\}/)) textNodes.push(node);
    }

    textNodes.forEach(function (textNode) {
      textNode.parentNode.replaceChild(codePlaceholderFragment(textNode.textContent), textNode);
    });
  }

  function enhanceCodePlaceholders(code) {
    if (code.dataset.codeBlankReady === "true") return;
    if (!code.textContent.match(/\{\{[^{}]+\}\}/)) return;
    code.dataset.codeBlankReady = "true";
    code.classList.add("code-blank-enabled");
    replacePlaceholdersInCode(code);
    initCodeBlanks(code);
  }

  function syncClipboardButton(button) {
    var target = button.getAttribute("data-clipboard-target");
    if (!target) return;

    var code = document.querySelector(target);
    if (!code || !code.classList.contains("code-blank-enabled")) return;

    button.setAttribute("data-clipboard-text", codeText(code));
  }

  function init() {
    document.querySelectorAll("pre > code").forEach(enhanceCodePlaceholders);
    syncSecondaryTocPassedLinks();
  }

  function activeSecondaryTocLink(links) {
    var active = document.querySelector(".md-sidebar--secondary .md-nav__link--active");
    if (active) return active;

    if (location.hash) {
      var matching = links.find(function (link) {
        return link.hash === location.hash;
      });
      if (matching) return matching;
    }

    return links[0] || null;
  }

  function syncSecondaryTocPassedLinks() {
    var links = Array.from(document.querySelectorAll(".md-sidebar--secondary .md-nav__link"));
    if (!links.length) return;

    var active = activeSecondaryTocLink(links);
    var activeIndex = active ? links.indexOf(active) : -1;

    links.forEach(function (link, index) {
      link.classList.toggle(
        "md-nav__link--passed",
        activeIndex > -1 && index < activeIndex
      );
    });
  }

  var syncTocQueued = false;
  function queueSecondaryTocSync() {
    if (syncTocQueued) return;

    syncTocQueued = true;
    requestAnimationFrame(function () {
      syncTocQueued = false;
      syncSecondaryTocPassedLinks();
    });
  }

  window.addEventListener("hashchange", queueSecondaryTocSync);
  window.addEventListener("scroll", queueSecondaryTocSync, { passive: true });

  var tocObserver = new MutationObserver(queueSecondaryTocSync);
  tocObserver.observe(document.documentElement, {
    subtree: true,
    attributes: true,
    attributeFilter: ["class"]
  });

  document.addEventListener("click", function (event) {
    var button = event.target.closest(".md-clipboard");
    if (button) syncClipboardButton(button);
  }, true);

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();

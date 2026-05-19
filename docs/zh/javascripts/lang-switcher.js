(function () {
  const MAP_URL = "/assets/lang-map.json";

  function normalizePath(pathname) {
    if (!pathname.endsWith("/")) return pathname + "/";
    return pathname;
  }

  function currentLang(pathname) {
    return pathname.startsWith("/zh/") ? "zh" : "en";
  }

  function fallbackPeer(pathname) {
    const normalized = normalizePath(pathname);
    if (normalized.startsWith("/zh/")) {
      const rest = normalized.slice(3);
      return rest || "/";
    }
    return "/zh" + normalized;
  }

  function mountSwitcher(map) {
    const header = document.querySelector(".md-header__option") ||
      document.querySelector(".md-header__inner") ||
      document.querySelector(".md-header");
    if (!header || document.querySelector(".linx-lang-switcher")) return;

    const pathname = normalizePath(window.location.pathname);
    const lang = currentLang(pathname);
    const peer = map[pathname] || fallbackPeer(pathname);

    const wrapper = document.createElement("div");
    wrapper.className = "linx-lang-switcher";
    wrapper.innerHTML = `
      <a href="${lang === "en" ? pathname : peer}" class="${lang === "en" ? "is-active" : ""}">EN</a>
      <span>/</span>
      <a href="${lang === "zh" ? pathname : peer}" class="${lang === "zh" ? "is-active" : ""}">中文</a>
    `;

    if (header.classList.contains("md-header__option")) {
      header.parentNode.insertBefore(wrapper, header);
    } else {
      header.appendChild(wrapper);
    }
  }

  fetch(MAP_URL)
    .then((resp) => (resp.ok ? resp.json() : {}))
    .then((map) => mountSwitcher(map))
    .catch(() => mountSwitcher({}));
})();

/* The full index and all links remain usable with scripting disabled. */
(() => {
  // Encoding-index links may target any form in a multi-form instruction.
  function showLinkedForm() {
    const target = document.getElementById(location.hash.slice(1));
    const variant = target?.closest("details.variant");
    if (variant && !variant.open) {
      variant.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener("hashchange", showLinkedForm);
  showLinkedForm();
  const controls = document.querySelector(".search");
  if (!controls) return;
  const input = controls.querySelector("input");
  const select = controls.querySelector("select");
  const status = controls.querySelector("output");
  const groups = Array.from(document.querySelectorAll("[data-section]"), group => ({
    group,
    jump: document.querySelector('a[href="#' + group.id + '"]'),
    entries: Array.from(group.querySelectorAll("[data-search]"))
  }));
  function filter() {
    const terms = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let total = 0;
    for (const {group, jump, entries} of groups) {
      let visible = 0;
      for (const entry of entries) {
        const match = terms.every(term => entry.dataset.search.includes(term))
          && (!select || !select.value || entry.dataset.kind === select.value);
        entry.hidden = !match;
        if (match) visible++;
      }
      group.hidden = visible === 0;
      if (jump) jump.hidden = group.hidden;
      total += visible;
    }
    status.textContent = total + " 项";
  }
  input.addEventListener("input", filter);
  if (select) select.addEventListener("change", filter);
  controls.hidden = false;
  filter();
})();

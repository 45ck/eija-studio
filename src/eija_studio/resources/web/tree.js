"use strict";
const EijaTree = (() => {
  function render(root, data, model, select) {
    const previous = root.querySelector('[tabindex="0"]')?.dataset.eijaId;
    root.replaceChildren(); root.setAttribute("role", "tree"); root.setAttribute("aria-label", "Domain explorer");
    const groups = [
      ["Language", "term", data.language?.terms || [], item => item.label || item.id],
      ["States", "state", (model?.states || []).map(id => ({id})), item => item.id],
      ["Transitions", "transition", model?.transitions || [], item => item.action],
      ["Roles", "role", data.roles || [], item => item.id],
      ["Laws", "law", data.laws || [], item => item.id]
    ];
    for (const [title, kind, items, label] of groups) {
      const section = document.createElement("div"); section.setAttribute("role", "treeitem"); section.setAttribute("aria-expanded", "true"); section.tabIndex = -1;
      section.className = "tree-group"; section.dataset.eijaId = `${data.pack.id}.group.${kind}`;
      const heading = document.createElement("span"); heading.textContent = `${title} (${items.length})`; section.append(heading);
      const children = document.createElement("div"); children.setAttribute("role", "group");
      for (const item of items) {
        const leaf = document.createElement("div"); leaf.setAttribute("role", "treeitem"); leaf.tabIndex = -1; leaf.setAttribute("aria-selected", "false");
        leaf.textContent = label(item); leaf.dataset.eijaId = `${data.pack.id}.${kind}.${item.id}`; leaf.className = "tree-leaf";
        const choose = () => {
          for (const n of root.querySelectorAll('[aria-selected]')) n.setAttribute("aria-selected", "false");
          leaf.setAttribute("aria-selected", "true"); select(kind, item);
        };
        leaf.addEventListener("click", choose);
        leaf.addEventListener("keydown", event => { if (["Enter", " "].includes(event.key)) {event.preventDefault(); event.stopPropagation(); choose();} });
        children.append(leaf);
      }
      section.append(children); root.append(section);
      heading.addEventListener("click", () => { const expanded = section.getAttribute("aria-expanded") === "true"; section.setAttribute("aria-expanded", String(!expanded)); children.hidden = expanded; });
    }
    const all = [...root.querySelectorAll('[role="treeitem"]')];
    (all.find(n => n.dataset.eijaId === previous) || all[0])?.setAttribute("tabindex", "0");
    root.onfocusin = event => { if (event.target.getAttribute("role") !== "treeitem") return; for (const node of all) node.tabIndex = node === event.target ? 0 : -1; };
    root.onkeydown = event => {
      const item = event.target.closest('[role="treeitem"]'); if (!item) return;
      const visible = all.filter(n => !n.closest('[role="group"][hidden]'));
      const index = visible.indexOf(item); let next;
      if (event.key === "ArrowDown") next = visible[Math.min(index + 1, visible.length - 1)];
      if (event.key === "ArrowUp") next = visible[Math.max(0, index - 1)];
      if (event.key === "Home") next = visible[0];
      if (event.key === "End") next = visible[visible.length - 1];
      const group = item.querySelector(':scope > [role="group"]');
      if (event.key === "ArrowRight" && group) {item.setAttribute("aria-expanded", "true"); group.hidden = false; next = group.firstElementChild;}
      if (event.key === "ArrowLeft") {if (group && !group.hidden) {item.setAttribute("aria-expanded", "false"); group.hidden = true; next = item;} else next = item.parentElement.closest('[role="treeitem"]');}
      if (next) {event.preventDefault(); event.stopPropagation(); next.focus();}
    };
  }
  return {render};
})();

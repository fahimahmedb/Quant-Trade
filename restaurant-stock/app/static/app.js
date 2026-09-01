// Améliorations progressives uniquement : toutes les pages fonctionnent sans JS
// (formulaires HTML classiques). Ceci ne fait qu'accélérer la saisie.

document.addEventListener("DOMContentLoaded", () => {
  // Comptage : sélectionne tout le contenu au focus pour que taper un chiffre
  // remplace la valeur pré-remplie au lieu de la compléter.
  document.querySelectorAll(".count-input").forEach((input) => {
    input.addEventListener("focus", () => input.select());

    const row = input.closest("[data-count-row]");
    const reasonWrap = row ? row.querySelector("[data-reason-wrap]") : null;
    if (!row || !reasonWrap) return;

    const theoretical = parseFloat(row.dataset.theoretical || "0");
    const toggleReason = () => {
      const value = parseFloat(input.value);
      if (Number.isNaN(value)) {
        reasonWrap.hidden = true;
        return;
      }
      const diff = Math.abs(value - theoretical);
      const relevant = theoretical !== 0 ? diff / Math.abs(theoretical) > 0.05 : diff > 0;
      reasonWrap.hidden = !relevant;
    };
    input.addEventListener("input", toggleReason);
    toggleReason();
  });

  // Fiche technique : ajout/suppression dynamique de lignes ingrédient.
  const addBtn = document.querySelector("[data-add-ingredient-row]");
  const rowsContainer = document.querySelector("[data-ingredient-rows]");
  if (addBtn && rowsContainer) {
    addBtn.addEventListener("click", () => {
      const template = rowsContainer.querySelector("[data-ingredient-row]");
      const clone = template.cloneNode(true);
      clone.querySelectorAll("input, select").forEach((el) => {
        if (el.tagName === "SELECT") el.selectedIndex = 0;
        else el.value = "";
      });
      rowsContainer.appendChild(clone);
    });

    rowsContainer.addEventListener("click", (event) => {
      if (event.target.matches("[data-remove-ingredient-row]")) {
        const rows = rowsContainer.querySelectorAll("[data-ingredient-row]");
        if (rows.length > 1) {
          event.target.closest("[data-ingredient-row]").remove();
        }
      }
    });
  }
});

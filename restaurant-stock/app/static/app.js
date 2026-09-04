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

  // Réception : le prix pré-rempli et les unités suivent l'ingrédient choisi.
  const syncDeliveryRow = (row) => {
    const select = row.querySelector("[data-ingredient-select]");
    if (!select || !select.options.length) return;
    const option = select.options[select.selectedIndex];
    const unitLabel = row.querySelector("[data-unit-label]");
    const priceUnitLabel = row.querySelector("[data-price-unit-label]");
    const priceInput = row.querySelector('input[name="unit_price"]');
    if (unitLabel) unitLabel.textContent = option.dataset.unit || "";
    if (priceUnitLabel) priceUnitLabel.textContent = "€/" + (option.dataset.priceUnit || "");
    if (priceInput) priceInput.value = option.dataset.lastPrice || "";
  };

  const deliveryRows = document.querySelector("[data-delivery-rows]");
  if (deliveryRows) {
    deliveryRows.querySelectorAll("[data-delivery-row]").forEach(syncDeliveryRow);
    deliveryRows.addEventListener("change", (event) => {
      if (event.target.matches("[data-ingredient-select]")) {
        syncDeliveryRow(event.target.closest("[data-delivery-row]"));
      }
    });
    const addDeliveryRow = document.querySelector("[data-add-delivery-row]");
    if (addDeliveryRow) {
      addDeliveryRow.addEventListener("click", () => {
        const template = deliveryRows.querySelector("[data-delivery-row]");
        const clone = template.cloneNode(true);
        clone.querySelectorAll("input").forEach((el) => (el.value = ""));
        const select = clone.querySelector("[data-ingredient-select]");
        if (select) select.selectedIndex = 0;
        deliveryRows.appendChild(clone);
        syncDeliveryRow(clone);
      });
    }
  }

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

  // Nom du fichier choisi : le bouton natif reste (accessibilité, fonctionne
  // sans JS via `<label for>`), seul son texte anglais du navigateur
  // (« Choose File », « No file chosen ») est masqué en CSS et remplacé ici.
  document.querySelectorAll("[data-champ-fichier]").forEach((champ) => {
    const input = champ.querySelector('input[type="file"]');
    const nom = champ.querySelector("[data-nom-fichier]");
    if (!input || !nom) return;
    const defaut = nom.textContent;
    input.addEventListener("change", () => {
      nom.textContent = input.files.length
        ? Array.from(input.files).map((f) => f.name).join(", ")
        : defaut;
    });
  });
});

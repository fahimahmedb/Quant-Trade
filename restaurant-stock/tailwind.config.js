/** @type {import('tailwindcss').Config} */
module.exports = {
  // Les scripts posent aussi des classes (bandeau hors-ligne de F3) :
  // sans eux, le style du bandeau dépendrait du hasard des gabarits.
  content: ["./app/templates/**/*.html", "./app/static/*.js"],
  theme: {
    // Palette remplacée, pas étendue : les couleurs Tailwind par défaut ne
    // sont plus disponibles. C'est délibéré — tant qu'un `bg-emerald-600`
    // reste écrivable, il finit par revenir. La direction visuelle V1.2 tient
    // en six valeurs, définies dans app/static/tailwind_src.css.
    colors: {
      transparent: "transparent",
      current: "currentColor",
      blanc: "#ffffff",
      fond: "var(--fond)",
      surface: "var(--surface)",
      encre: "var(--encre)",
      "encre-doux": "var(--encre-doux)",
      accent: "var(--accent)",
      "accent-fond": "var(--accent-fond)",
      alerte: "var(--alerte)",
      "alerte-fond": "var(--alerte-fond)",
      valide: "var(--valide)",
      "valide-fond": "var(--valide-fond)",
      structure: "var(--structure)",
      filet: "var(--filet)",

      /* --- Relais transitoire, à supprimer au lot 4 --------------------
         Le lot 1 ne redessine que deux écrans témoins. Les douze autres
         écrivent encore `bg-white`, `text-gray-500`, `bg-emerald-600`.
         Sans ces alias, supprimer la palette Tailwind les laisserait sans
         style du jour au lendemain — un faux problème qui parasiterait la
         validation de la direction visuelle.

         Ces noms pointent donc vers les jetons V1.2 : le vert Tailwind
         disparaît partout immédiatement, sans que personne ait à repasser
         sur quatorze écrans avant que la direction soit validée. Chaque
         écran migré au fil des lots 2 à 4 abandonne ces noms ; quand il
         n'en reste plus, ce bloc part avec eux.

         Un cas reste en suspens : `blue-600` servait à distinguer un
         surplus d'un manquant sur l'écran d'écarts. La direction n'admet
         qu'une couleur de statut d'alerte, donc le surplus retombe ici en
         encre neutre. C'est une perte d'information à trancher en U6. */
      white: "var(--surface)",
      "gray-50": "var(--fond)",
      "gray-100": "var(--fond)",
      "gray-200": "var(--filet)",
      "gray-400": "var(--encre-doux)",
      "gray-500": "var(--encre-doux)",
      "gray-600": "var(--encre-doux)",
      "gray-900": "var(--encre)",
      "slate-300": "var(--structure)",
      "slate-600": "var(--encre-doux)",
      "slate-700": "var(--encre)",
      "slate-800": "var(--encre)",
      "emerald-50": "var(--valide-fond)",
      "emerald-300": "var(--valide)",
      "emerald-500": "var(--accent)",
      "emerald-600": "var(--accent)",
      "emerald-700": "var(--valide)",
      "red-100": "var(--alerte-fond)",
      "red-500": "var(--alerte)",
      "red-600": "var(--alerte)",
      "red-700": "var(--alerte)",
      "amber-50": "var(--alerte-fond)",
      "amber-300": "var(--alerte)",
      "amber-600": "var(--alerte)",
      "amber-700": "var(--alerte)",
      "amber-800": "var(--alerte)",
      "blue-600": "var(--encre)",
    },
    // Angle presque droit partout : une étiquette de bac, pas une carte.
    borderRadius: {
      none: "0",
      DEFAULT: "3px",
      sm: "2px",
      full: "9999px",
    },
    // Aucune ombre portée dans la direction visuelle. La structure vient du
    // filet ; laisser `shadow` disponible reviendrait à le réintroduire.
    boxShadow: {
      none: "none",
    },
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "SF Mono", "Menlo", "monospace"],
      },
      // Échelle explicite. L'écart entre `saisie` (le texte lu debout, à bout
      // de bras) et `base` est le rapport qui compte : 24 px contre 15 px.
      fontSize: {
        contexte: ["0.8125rem", { lineHeight: "1.15rem" }],
        base: ["0.9375rem", { lineHeight: "1.35rem" }],
        titre2: ["1.0625rem", { lineHeight: "1.4rem" }],
        titre1: ["1.25rem", { lineHeight: "1.6rem" }],
        saisie: ["1.5rem", { lineHeight: "1.85rem" }],
        montant: ["1.75rem", { lineHeight: "2rem" }],
        chiffre: ["2.25rem", { lineHeight: "2.4rem" }],
      },
    },
  },
  plugins: [],
};

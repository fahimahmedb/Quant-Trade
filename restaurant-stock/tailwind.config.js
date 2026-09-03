/** @type {import('tailwindcss').Config} */
module.exports = {
  // Les scripts posent aussi des classes (bandeau hors-ligne de F3) :
  // sans eux, le style du bandeau dépendrait du hasard des gabarits.
  content: ["./app/templates/**/*.html", "./app/static/*.js"],
  theme: {
    // --- Rythme d'espacement --------------------------------------------
    // Conservé de la révision précédente, c'est ce qui tient la régularité.
    // L'échelle est remplacée, pas étendue : les crans fractionnaires de
    // Tailwind (0.5 = 2 px, 1.5 = 6 px…) n'existent plus, donc une valeur
    // hors de l'échelle de 4 px n'est pas seulement interdite, elle est
    // inécrivable — `p-2.5` ne produit rien et se voit.
    spacing: {
      0: "0px",
      1: "4px",
      2: "8px",
      3: "12px",
      4: "16px",
      5: "20px",
      6: "24px",
      7: "28px",
      8: "32px",
      9: "36px",
      10: "40px",
      11: "44px",
      12: "48px",
      13: "52px",
      14: "56px",
      16: "64px",
      18: "72px",
      20: "80px",
      24: "96px",
    },

    // --- Rayons -----------------------------------------------------------
    // La contrainte « deux rayons au maximum » de la révision précédente ne
    // survit pas à celle-ci : la direction native demande des cercles pleins
    // (pastilles, actions rapides) et un grand arrondi bas pour le héros.
    // Les rayons de carte génériques, eux, ont disparu avec les cartes.
    borderRadius: {
      none: "0px",
      DEFAULT: "12px",
      champ: "12px",
      heros: "28px",
      cercle: "9999px",
    },

    // Aucune ombre portée : c'est l'un des marqueurs du système rejeté.
    // La seule ombre du projet est la lueur de focus d'un champ, écrite à la
    // main dans tailwind_src.css.
    boxShadow: {
      none: "none",
    },

    colors: {
      transparent: "transparent",
      current: "currentColor",
      blanc: "var(--blanc)",
      encre: "var(--encre)",
      gris: "var(--gris)",
      trait: "var(--trait)",
      appui: "var(--appui)",
      accent: "var(--accent)",
      "accent-clair": "var(--accent-clair)",
      alerte: "var(--alerte)",
      "alerte-clair": "var(--alerte-clair)",
      valide: "var(--valide)",
      "valide-clair": "var(--valide-clair)",

      /* --- Relais transitoire, à supprimer quand tous les écrans auront
         migré. La révision 2 ne redessine que l'accueil ; les autres écrans
         écrivent encore `bg-white`, `text-gray-500`, `bg-emerald-600`. Ces
         noms pointent vers les jetons de la nouvelle direction, pour qu'ils
         restent lisibles sans avoir été retouchés.

         Les anciens noms de la direction précédente (`surface`, `structure`,
         `filet`, `fond`) ne figurent plus : ils désignaient le système de
         cartes sur fond gris, qui a été retiré et non remplacé. */
      white: "var(--blanc)",
      "gray-50": "var(--blanc)",
      "gray-100": "var(--appui)",
      "gray-200": "var(--trait)",
      "gray-400": "var(--gris)",
      "gray-500": "var(--gris)",
      "gray-600": "var(--gris)",
      "gray-900": "var(--encre)",
      "slate-300": "var(--gris)",
      "slate-600": "var(--gris)",
      "slate-700": "var(--encre)",
      "slate-800": "var(--encre)",
      "emerald-50": "var(--valide-clair)",
      "emerald-100": "var(--valide-clair)",
      "emerald-300": "var(--valide)",
      "emerald-500": "var(--accent)",
      "emerald-600": "var(--accent)",
      "emerald-700": "var(--valide)",
      "red-100": "var(--alerte-clair)",
      "red-500": "var(--alerte)",
      "red-600": "var(--alerte)",
      "red-700": "var(--alerte)",
      "amber-50": "var(--alerte-clair)",
      "amber-100": "var(--alerte-clair)",
      "amber-300": "var(--alerte)",
      "amber-600": "var(--alerte)",
      "amber-700": "var(--alerte)",
      "amber-800": "var(--alerte)",
      "blue-600": "var(--encre)",
    },

    extend: {
      // `minHeight` n'hérite pas de `spacing` en Tailwind 3 : on l'y
      // raccroche pour que les cibles tactiles s'écrivent dans la même
      // échelle que le reste (`min-h-12` = 48 px).
      minHeight: ({ theme }) => ({ ...theme("spacing"), full: "100%", screen: "100vh" }),
      fontFamily: {
        sans: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "SF Mono", "Menlo", "monospace"],
      },
      fontSize: {
        micro: ["11px", { lineHeight: "16px" }],
        contexte: ["13px", { lineHeight: "18px" }],
        base: ["15px", { lineHeight: "21px" }],
        corps: ["16px", { lineHeight: "21px" }],
        titre2: ["17px", { lineHeight: "24px" }],
        titre1: ["21px", { lineHeight: "28px" }],
        saisie: ["24px", { lineHeight: "32px" }],
        ecran: ["34px", { lineHeight: "40px" }],
        heros: ["52px", { lineHeight: "56px" }],
      },
    },
  },
  plugins: [],
};

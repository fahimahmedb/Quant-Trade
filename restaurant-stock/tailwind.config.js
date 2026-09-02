/** @type {import('tailwindcss').Config} */
module.exports = {
  // Les scripts posent aussi des classes (bandeau hors-ligne de F3) :
  // sans eux, le style du bandeau dépendrait du hasard des gabarits.
  content: ["./app/templates/**/*.html", "./app/static/*.js"],
  theme: {
    // --- Rythme d'espacement (AC-D-1) -----------------------------------
    // L'échelle est remplacée, pas étendue : les crans fractionnaires de
    // Tailwind (0.5 = 2 px, 1.5 = 6 px, 2.5 = 10 px…) n'existent plus. Une
    // valeur hors de l'échelle de 4 px n'est donc pas seulement interdite,
    // elle est inécrivable — `p-2.5` ne produit plus rien et se voit.
    // C'est la règle la plus importante de la direction : l'irrégularité des
    // marges est ce qui se lit comme « bâclé », avant même la couleur.
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

    // --- Deux rayons, pas trois (AC-D-2) --------------------------------
    // 12 px pour un bloc, 8 px pour ce qui vit à l'intérieur. `rounded-full`
    // est retiré : c'était la troisième valeur.
    borderRadius: {
      none: "0px",
      DEFAULT: "8px",
      champ: "8px",
      bloc: "12px",
    },

    // Aucune ombre portée. Un bloc au repos porte une seule des trois
    // marques possibles, et c'est son fond. La seule ombre du projet est la
    // lueur de focus d'un champ, écrite à la main dans tailwind_src.css.
    boxShadow: {
      none: "none",
    },

    colors: {
      transparent: "transparent",
      current: "currentColor",
      blanc: "#ffffff",
      fond: "var(--fond)",
      surface: "var(--surface)",
      champ: "var(--champ)",
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
         Le lot 1 ne redessine que deux écrans témoins. Les autres écrivent
         encore `bg-white`, `text-gray-500`, `bg-emerald-600`. Ces noms
         pointent vers les jetons V1.2 : le vert Tailwind disparaît partout
         immédiatement, sans qu'il faille repasser sur quatorze écrans avant
         que la direction soit validée. Chaque écran migré au fil des lots 2
         à 4 abandonne ces noms ; quand il n'en reste plus, ce bloc part.

         Un cas reste en suspens : `blue-600` distinguait un surplus d'un
         manquant sur l'écran d'écarts. La direction n'admet qu'une couleur
         d'alerte, donc le surplus retombe en encre neutre — perte
         d'information à trancher en U6. */
      white: "var(--surface)",
      "gray-50": "var(--fond)",
      "gray-100": "var(--champ)",
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
      "emerald-100": "var(--valide-fond)",
      "emerald-300": "var(--valide)",
      "emerald-500": "var(--accent)",
      "emerald-600": "var(--accent)",
      "emerald-700": "var(--valide)",
      "red-100": "var(--alerte-fond)",
      "red-500": "var(--alerte)",
      "red-600": "var(--alerte)",
      "red-700": "var(--alerte)",
      "amber-50": "var(--alerte-fond)",
      "amber-100": "var(--alerte-fond)",
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
      // Deux graisses suffisent au texte courant ; le gras lourd est réservé
      // aux montants. L'échelle reste explicite : `montant` et `chiffre` ne
      // servent qu'aux euros, qui sont l'élément le plus fort de l'écran.
      fontSize: {
        micro: ["0.6875rem", { lineHeight: "1rem" }],
        contexte: ["0.8125rem", { lineHeight: "1.125rem" }],
        base: ["0.9375rem", { lineHeight: "1.375rem" }],
        titre2: ["1.0625rem", { lineHeight: "1.5rem" }],
        titre1: ["1.25rem", { lineHeight: "1.75rem" }],
        saisie: ["1.5rem", { lineHeight: "2rem" }],
        montant: ["1.75rem", { lineHeight: "2rem" }],
        chiffre: ["2.25rem", { lineHeight: "2.5rem" }],
      },
    },
  },
  plugins: [],
};

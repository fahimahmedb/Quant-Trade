/** @type {import('tailwindcss').Config} */
module.exports = {
  // Les scripts posent aussi des classes (bandeau hors-ligne de F3) :
  // sans eux, le style du bandeau dépendrait du hasard des gabarits.
  content: ["./app/templates/**/*.html", "./app/static/*.js"],
  theme: {
    extend: {},
  },
  plugins: [],
};

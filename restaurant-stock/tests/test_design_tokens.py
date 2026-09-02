"""Direction visuelle V1.2 — les jetons de couleur tiennent leurs contrastes.

L'écran est consulté sous néon de cuisine, souvent de biais et à bout de bras.
Les seuils ci-dessous sont donc plus exigeants que le minimum réglementaire
pour le texte courant : AAA (7:1) au lieu de AA (4.5:1).

Ce test lit les valeurs dans la feuille de style, pas une copie : retoucher une
couleur sans rejouer les contrastes fera échouer la suite.
"""
import re
from pathlib import Path

import pytest

CSS = Path(__file__).resolve().parent.parent / "app" / "static" / "tailwind_src.css"


def _tokens() -> dict[str, str]:
    """Les variables CSS `--nom: #rrggbb;` déclarées dans `:root`."""
    source = CSS.read_text()
    root = source.split(":root {", 1)[1].split("\n  }", 1)[0]
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6});", root))


def _relative_luminance(hex_color: str) -> float:
    channels = []
    for pair in (hex_color[1:3], hex_color[3:5], hex_color[5:7]):
        c = int(pair, 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast(a: str, b: str) -> float:
    la, lb = _relative_luminance(a), _relative_luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


BLANC = "#ffffff"

# (texte, fond, seuil, raison)
CONTRASTS = [
    ("encre", "surface", 7.0, "texte courant sur un bloc"),
    ("encre", "fond", 7.0, "texte courant sur la page"),
    ("encre-doux", "surface", 4.5, "texte secondaire sur un bloc"),
    ("encre-doux", "fond", 4.5, "texte secondaire sur la page"),
    ("alerte", "surface", 4.5, "montant d'écart sur un bloc"),
    ("alerte", "alerte-fond", 4.5, "texte d'alerte sur son propre fond"),
    ("valide", "surface", 4.5, "statut conforme sur un bloc"),
    ("valide", "valide-fond", 4.5, "texte validé sur son propre fond"),
    ("accent", "surface", 4.5, "lien d'action sur un bloc"),
    ("accent", "accent-fond", 4.5, "texte d'accent sur son propre fond"),
]


@pytest.mark.parametrize("avant, arriere, seuil, raison", CONTRASTS)
def test_contrast_is_sufficient_under_kitchen_lighting(avant, arriere, seuil, raison):
    tokens = _tokens()
    ratio = _contrast(tokens[avant], tokens[arriere])
    assert ratio >= seuil, f"{raison} : {avant}/{arriere} = {ratio:.2f}, minimum {seuil}"


@pytest.mark.parametrize("fond", ["accent", "alerte", "valide", "encre"])
def test_white_text_is_readable_on_every_filled_background(fond):
    """Les surfaces pleines (bouton d'accent, bandeau, en-tête) portent du
    texte blanc : il doit rester lisible sur chacune."""
    ratio = _contrast(BLANC, _tokens()[fond])
    assert ratio >= 4.5, f"blanc sur {fond} = {ratio:.2f}"


def test_structure_hairline_is_visible_without_being_a_border_of_shame():
    """Le filet remplace l'ombre portée pour délimiter un bloc : il doit se
    voir. Le seuil de 3:1 de la WCAG vise les composants porteurs d'état, pas
    un séparateur — on exige donc qu'il se distingue nettement des deux fonds,
    sans le noircir au point d'alourdir la page."""
    tokens = _tokens()
    for arriere in ("surface", "fond"):
        ratio = _contrast(tokens["structure"], tokens[arriere])
        assert 1.7 <= ratio <= 3.5, f"structure/{arriere} = {ratio:.2f}"


def test_the_six_named_values_of_the_visual_direction_are_all_defined():
    """La direction tient en six valeurs. Si l'une disparaît ou si une
    septième apparaît sans être une teinte dérivée, c'est un changement de
    direction, pas une retouche."""
    tokens = _tokens()
    fondamentales = {"fond", "encre", "accent", "alerte", "valide", "structure"}
    derivees = {"surface", "encre-doux", "filet", "accent-fond", "alerte-fond", "valide-fond"}
    assert fondamentales <= set(tokens)
    assert set(tokens) == fondamentales | derivees


def test_no_tailwind_default_green_survives_in_the_templates():
    """« Le vert Tailwind actuel doit disparaître : il ne veut rien dire. »

    Les gabarits migrés n'écrivent plus de couleur Tailwind du tout. Ceux qui
    en écrivent encore passent par les alias de `tailwind.config.js`, qui
    pointent vers les jetons — mais aucun ne doit produire un vert générique.
    """
    config = (CSS.parent.parent.parent / "tailwind.config.js").read_text()
    alias = re.findall(r'"(emerald|green)-\d+":\s*"var\(--([a-z-]+)\)"', config)
    assert alias, "les alias de vert doivent rester explicites tant qu'ils existent"
    for nom, cible in alias:
        assert cible in {"accent", "valide", "valide-fond"}, (
            f"{nom} pointe vers {cible} : un vert Tailwind ne doit jamais "
            "ressortir tel quel"
        )

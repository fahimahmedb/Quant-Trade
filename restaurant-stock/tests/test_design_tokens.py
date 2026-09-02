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
    derivees = {"surface", "champ", "encre-doux", "filet",
                "accent-fond", "alerte-fond", "valide-fond"}
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


# ==========================================================================
# Règles de finition V1.2 (AC-D-1 à AC-D-8).
#
# Ces tests portent sur la feuille de style et les gabarits, pas sur le rendu :
# ils empêchent une valeur hors échelle ou un troisième rayon de revenir sans
# qu'on s'en aperçoive. Ce qui demande un vrai navigateur (débordement de la
# navigation) est vérifié dans tests/test_nr_mobile.py.
# ==========================================================================

RACINE = CSS.parent.parent.parent
CONFIG = RACINE / "tailwind.config.js"
GABARITS = sorted((RACINE / "app" / "templates").rglob("*.html"))


def test_ac_d_1_every_spacing_step_is_a_multiple_of_four_pixels():
    """L'irrégularité des marges est ce qui se lit comme « bâclé ».

    L'échelle est verrouillée dans la configuration : un cran hors échelle
    n'est pas seulement interdit, il est inécrivable dans un gabarit.
    """
    bloc = CONFIG.read_text().split("spacing: {", 1)[1].split("},", 1)[0]
    valeurs = re.findall(r":\s*\"(\d+)px\"", bloc)
    assert valeurs, "l'échelle d'espacement doit rester explicite"
    hors_echelle = [v for v in valeurs if int(v) % 4 != 0]
    assert hors_echelle == [], f"crans hors échelle de 4 px : {hors_echelle}"


def test_ac_d_1_stylesheet_spacing_declarations_stay_on_the_scale():
    """Les composants écrits à la main doivent suivre la même échelle que les
    classes utilitaires, sinon la règle ne vaut que pour la moitié du style."""
    source = CSS.read_text()
    fautes = []
    for prop, valeur in re.findall(
        r"\b(padding|margin|gap|min-height)(?:-[a-z]+)?:\s*([^;]+);", source
    ):
        for px in re.findall(r"(\d+)px", valeur):
            if int(px) % 4 != 0:
                fautes.append(f"{prop}: {valeur.strip()}")
    assert fautes == [], f"espacements hors échelle de 4 px : {fautes}"


def test_ac_d_1_templates_use_no_off_scale_arbitrary_spacing():
    """Une valeur arbitraire (`top-[92px]`) contourne l'échelle : elle doit
    rester dessus, sinon la configuration ne protège plus rien."""
    fautes = []
    for gabarit in GABARITS:
        for utilitaire, px in re.findall(
            r"\b([a-z]+(?:-[a-z]+)?)-\[(\d+)px\]", gabarit.read_text()
        ):
            if int(px) % 4 != 0:
                fautes.append(f"{gabarit.name}: {utilitaire}-[{px}px]")
    assert fautes == [], f"valeurs arbitraires hors échelle : {fautes}"


def test_ac_d_2_at_most_two_corner_radii_in_the_whole_application():
    """Un rayon pour le bloc, un pour ce qui vit dedans. Jamais un troisième."""
    bloc = CONFIG.read_text().split("borderRadius: {", 1)[1].split("},", 1)[0]
    rayons = {v for v in re.findall(r":\s*\"(\d+)px\"", bloc) if v != "0"}
    assert len(rayons) <= 2, f"trois rayons ou plus : {sorted(rayons)}"

    dans_le_style = {
        v for v in re.findall(r"border-radius:\s*(\d+)px", CSS.read_text()) if v != "0"
    }
    assert dans_le_style <= rayons, (
        f"la feuille de style introduit un rayon absent de l'échelle : "
        f"{sorted(dans_le_style - rayons)}"
    )


@pytest.mark.parametrize(
    "selecteur",
    [".btn:active", ".btn-tertiaire:active", ".onglet:active",
     ".champ:focus-within", ".select:focus", ":focus-visible"],
)
def test_ac_d_3_interactive_elements_react_to_touch_and_to_focus(selecteur):
    """Sans état pressé, l'interface paraît morte au doigt ; sans état de
    focus, elle est inutilisable au clavier."""
    assert selecteur in CSS.read_text(), f"{selecteur} n'est défini nulle part"


def test_ac_d_4_counting_field_and_touch_targets_are_large_enough():
    """La tension avec la référence bancaire est tranchée en faveur de la
    cuisine : mains froides, gants, écran gras."""
    source = CSS.read_text()

    def min_height(bloc: str) -> int:
        corps = source.split(bloc + " {", 1)[1].split("}", 1)[0]
        return int(re.search(r"min-height:\s*(\d+)px", corps).group(1))

    assert min_height(".champ") >= 52, "le champ de comptage doit faire 52 px"
    assert min_height(".btn") >= 52, "un bouton doit faire 52 px"
    for cible in (".btn-tertiaire", ".onglet", ".select"):
        assert min_height(cible) >= 48, f"{cible} sous la cible tactile de 48 px"


def test_ac_d_7_nothing_animates_without_a_user_action():
    """Aucune animation d'entrée, aucun effet au survol : seules les
    transitions d'état existent, et la préférence système les coupe."""
    source = CSS.read_text()
    assert "@media (prefers-reduced-motion: reduce)" in source

    # Une transition ne se déclenche que sur un changement d'état ; une
    # `animation` part toute seule au chargement.
    animations = re.findall(r"^\s*animation:\s*[^;]+;", source, flags=re.M)
    assert animations == [], f"animation automatique : {animations}"

    # Le survol n'existe pas sur un écran tactile : le styler donne un état
    # collant après le toucher.
    survols = re.findall(r"^[^@\n]*:hover[^{]*\{", source, flags=re.M)
    assert survols == [], f"effet au survol : {survols}"

    for gabarit in GABARITS:
        texte = gabarit.read_text()
        assert "hover:" not in texte, f"{gabarit.name} utilise un effet au survol"
        assert "animate-" not in texte, f"{gabarit.name} déclenche une animation"


def test_ac_d_8_no_trailing_arrows_and_no_middot_separators():
    """Deux tics d'interface : la flèche collée en fin de libellé et le point
    médian qui sépare des métadonnées. Le libellé se suffit, la virgule aussi."""
    fautes = []
    for gabarit in GABARITS:
        texte = gabarit.read_text()
        if "·" in texte:
            fautes.append(f"{gabarit.name} : séparateur « · »")
        if "→" in texte:
            fautes.append(f"{gabarit.name} : flèche « → »")
    assert fautes == [], fautes


@pytest.mark.parametrize("etat", ["propose", "confirme"])
def test_counting_field_distinguishes_proposed_from_confirmed(etat):
    """Le champ dit s'il porte une valeur pré-remplie que personne n'a encore
    confirmée, ou une valeur enregistrée. Sans cette différence, le chef ne
    sait pas ce qui lui reste à faire."""
    assert f'.champ[data-etat="{etat}"]' in CSS.read_text()

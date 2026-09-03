"""Direction visuelle V1.2 — révision 2 : natif iOS + finition bancaire.

Remplace intégralement l'ancien fichier de contraste (jetons `surface` /
`structure` / `filet`, système de cartes sur fond gris) : ce système a été
retiré, pas complété, et ses tests n'ont plus d'objet.

L'écran est consulté sous néon de cuisine, souvent de biais et à bout de
bras : les seuils sont plus exigeants que le minimum réglementaire pour le
texte courant — AAA (7:1) au lieu de AA (4.5:1).

Ce test lit les valeurs dans la feuille de style, pas une copie : retoucher
une couleur sans rejouer les contrastes fera échouer la suite.
"""
import re
from pathlib import Path

import pytest

CSS = Path(__file__).resolve().parent.parent / "app" / "static" / "tailwind_src.css"
RACINE = CSS.parent.parent.parent
CONFIG = RACINE / "tailwind.config.js"
GABARITS = sorted((RACINE / "app" / "templates").rglob("*.html"))


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


def _composite(fg_rgba: str, bg_hex: str) -> str:
    """Couleur réellement affichée quand `fg_rgba` (blanc à X %) est posé sur
    `bg_hex`. Nécessaire pour la ligne secondaire du héros, écrite en blanc
    atténué : son contraste réel dépend de ce qui est dessous, pas du blanc
    pur déclaré dans la règle CSS."""
    match = re.search(
        r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", fg_rgba
    )
    fr, fg, fb, alpha = (float(x) for x in match.groups())
    bg = bg_hex.lstrip("#")
    br, bgc, bb = (int(bg[i : i + 2], 16) for i in (0, 2, 4))
    out = [round(alpha * f + (1 - alpha) * b) for f, b in ((fr, br), (fg, bgc), (fb, bb))]
    return "#%02x%02x%02x" % tuple(out)


BLANC = "#ffffff"


# ==========================================================================
# Le fond est blanc, pas une carte flottante (AC-D2-1 / point 0 et 2 de la
# révision) : ces tests portent donc sur le texte contre du blanc pur, pas
# contre un jeton `surface` intermédiaire qui n'existe plus.
# ==========================================================================

TEXTE_SUR_BLANC = [
    ("encre", 7.0, "texte courant"),
    ("gris", 4.5, "texte secondaire"),
    ("accent", 4.5, "lien d'action"),
    ("alerte", 4.5, "montant d'écart dans une liste"),
    ("valide", 4.5, "statut conforme dans une liste"),
]


@pytest.mark.parametrize("jeton, seuil, raison", TEXTE_SUR_BLANC)
def test_text_on_white_meets_its_threshold(jeton, seuil, raison):
    tokens = _tokens()
    ratio = _contrast(tokens[jeton], BLANC)
    assert ratio >= seuil, f"{raison} : {jeton}/blanc = {ratio:.2f}, minimum {seuil}"


# ==========================================================================
# Les pastilles : icône sur fond teinté clair (TC-D2-03). Testées dans les
# deux sens, comme une pastille doit l'être : l'icône doit se voir sur son
# fond, et ce même fond doit se distinguer du blanc qui l'entoure.
# ==========================================================================

PASTILLES = [
    ("accent", "accent-clair"),
    ("alerte", "alerte-clair"),
    ("valide", "valide-clair"),
]


@pytest.mark.parametrize("icone, fond", PASTILLES)
def test_pastille_icon_is_readable_on_its_tinted_background(icone, fond):
    tokens = _tokens()
    ratio = _contrast(tokens[icone], tokens[fond])
    assert ratio >= 4.5, f"pastille {icone}/{fond} = {ratio:.2f}"


@pytest.mark.parametrize("icone, fond", PASTILLES)
def test_pastille_background_is_distinguishable_from_white(icone, fond):
    """Une pastille dont le fond est confondu avec la page ne serait plus une
    pastille : elle doit rester visible sans dépendre de son icône."""
    tokens = _tokens()
    ratio = _contrast(tokens[fond], BLANC)
    assert ratio >= 1.1, f"fond de pastille {fond} indiscernable du blanc : {ratio:.3f}"


# ==========================================================================
# Le héros : le seul bloc plein-couleur de l'écran (TC-D2-02). Le contraste
# du texte blanc est vérifié sur le HAUT du dégradé, qui est le cas le plus
# défavorable puisque c'est la teinte la plus claire des deux.
# ==========================================================================


def test_hero_full_white_text_meets_aaa_on_the_lightest_point_of_the_gradient():
    """Le chiffre principal du héros (AC-D2-3 : jamais une perte) doit rester
    lisible même sur le point le plus clair du dégradé."""
    tokens = _tokens()
    ratio = _contrast(BLANC, tokens["heros-haut"])
    assert ratio >= 7.0, f"blanc/heros-haut = {ratio:.2f}"


def test_hero_secondary_line_meets_double_a_despite_its_reduced_opacity():
    """La ligne secondaire (l'indicateur défavorable) est en blanc atténué à
    72 % — vérifié sur la vraie couleur composée, pas sur le blanc pur."""
    source = CSS.read_text()
    attenue = re.search(r"--heros-attenue:\s*(rgba\([^;]+\));", source).group(1)
    tokens = _tokens()
    couleur_reelle = _composite(attenue, tokens["heros-haut"])
    ratio = _contrast(couleur_reelle, tokens["heros-haut"])
    assert ratio >= 4.5, f"blanc atténué/heros-haut = {ratio:.2f} (composé : {couleur_reelle})"


def test_hero_never_uses_alert_red_for_its_own_text():
    """« Le rouge reste réservé aux lignes de liste sur fond blanc, pas
    répété ici » (section 5). La couleur d'alerte ne doit apparaître dans
    aucune règle `.heros*`."""
    source = CSS.read_text()
    bloc_heros = "\n".join(
        ligne for ligne in source.splitlines() if re.match(r"\s*\.heros", ligne)
        or (ligne.strip().startswith((".", "}")) is False and "heros" in source)
    )
    # Extraction précise : chaque règle .heros* jusqu'à son accolade fermante.
    regles = re.findall(r"(\.heros[a-z-]*\s*\{[^}]*\})", source)
    assert regles, "au moins une règle .heros doit exister"
    for regle in regles:
        assert "var(--alerte)" not in regle, f"rouge d'alerte utilisé dans le héros : {regle}"


# ==========================================================================
# Les six teintes fondamentales existent toujours, dérivées comprises. Si
# l'une disparaît ou si une septième apparaît sans être une dérivée déclarée,
# c'est un changement de direction, pas une retouche.
# ==========================================================================


def test_the_named_tokens_of_the_visual_direction_are_exactly_these():
    tokens = _tokens()
    attendus = {
        "blanc", "encre", "gris", "trait", "appui",
        "heros-haut", "heros-bas",
        "accent", "accent-clair", "alerte", "alerte-clair", "valide", "valide-clair",
    }
    assert set(tokens) == attendus, (
        f"jetons inattendus : {set(tokens) - attendus} | "
        f"jetons manquants : {attendus - set(tokens)}"
    )


def test_no_leftover_card_system_tokens_survive():
    """Le système de cartes/ombres/jetons de la direction précédente
    (`surface`, `structure`, `filet`, `fond`, `champ` en couleur nommée) a été
    retiré, pas complété. Sa réapparition serait un retour en arrière."""
    tokens = _tokens()
    for fantome in ("surface", "structure", "filet", "fond"):
        assert fantome not in tokens, f"jeton de l'ancien système encore présent : {fantome}"

    config = CONFIG.read_text()
    bloc_colors = config.split("colors: {", 1)[1].split("\n    },", 1)[0]
    for fantome in ('"surface"', '"structure"', '"filet"', '"fond"'):
        assert fantome not in bloc_colors, f"alias de couleur fantôme : {fantome}"


def test_no_box_shadow_other_than_the_explicit_none():
    """Aucune ombre portée dans cette direction : la seule aurait été le
    marqueur du système de cartes rejeté par les captures de référence."""
    source = CSS.read_text()
    ombres = re.findall(r"box-shadow:\s*([^;]+);", source)
    for regle in ombres:
        assert "rgba(0, 0, 0" not in regle or "0 0 0 3px rgba(28, 74, 110" in regle, (
            f"ombre grise détectée : {regle}"
        )


# ==========================================================================
# Rythme d'espacement et rayons — repris de la révision précédente, ils ne
# bougent pas. Un rayon de carte générique n'a plus de raison d'exister,
# mais le héros et les cercles pleins (pastilles, actions rapides) demandent
# des valeurs que l'ancienne contrainte « deux rayons au maximum » aurait
# interdites : elle n'est donc pas reconduite telle quelle.
# ==========================================================================


def test_spacing_scale_stays_a_multiple_of_four_pixels():
    bloc = CONFIG.read_text().split("spacing: {", 1)[1].split("},", 1)[0]
    valeurs = re.findall(r":\s*\"(\d+)px\"", bloc)
    assert valeurs, "l'échelle d'espacement doit rester explicite"
    hors_echelle = [v for v in valeurs if int(v) % 4 != 0]
    assert hors_echelle == [], f"crans hors échelle de 4 px : {hors_echelle}"


def test_templates_use_no_off_scale_arbitrary_spacing():
    fautes = []
    for gabarit in GABARITS:
        for utilitaire, px in re.findall(
            r"\b([a-z]+(?:-[a-z]+)?)-\[(\d+)px\]", gabarit.read_text()
        ):
            if int(px) % 4 != 0:
                fautes.append(f"{gabarit.name}: {utilitaire}-[{px}px]")
    assert fautes == [], f"valeurs arbitraires hors échelle : {fautes}"


# ==========================================================================
# Retour au toucher et accessibilité (AC-D2-5, TC-D2-04, TC-D2-05, TC-D2-06).
# ==========================================================================


@pytest.mark.parametrize(
    "selecteur",
    [".btn:active", ".btn-tertiaire:active", ".onglet:active", ".ligne:active",
     ".action-rapide:active .action-rapide-cercle",
     ".champ:focus-within", ".select:focus", ":focus-visible"],
)
def test_interactive_elements_react_to_touch_and_to_focus(selecteur):
    """Sans état pressé, l'interface paraît morte au doigt ; sans état de
    focus, elle est inutilisable au clavier."""
    assert selecteur in CSS.read_text(), f"{selecteur} n'est défini nulle part"


def test_quick_action_touch_target_is_at_least_48px_regardless_of_circle_size():
    """AC-D2-5 : le cercle visuel peut être plus petit que 48 px, la cible
    touchable ne le peut pas."""
    source = CSS.read_text()
    regle_action = re.search(r"\.action-rapide\s*\{([^}]*)\}", source).group(1)
    assert re.search(r"min-height:\s*48px", regle_action), (
        "la zone touchable de .action-rapide doit faire au moins 48 px"
    )
    regle_cercle = re.search(r"\.action-rapide-cercle\s*\{([^}]*)\}", source).group(1)
    largeur = int(re.search(r"width:\s*(\d+)px", regle_cercle).group(1))
    assert largeur <= 52, (
        "le cercle est censé être visuellement plus petit que la cible tactile"
    )


def test_reduced_motion_preference_is_respected():
    assert "@media (prefers-reduced-motion: reduce)" in CSS.read_text()


def test_nothing_animates_without_a_user_action():
    """Aucune animation d'entrée, aucun effet au survol : seules les
    transitions d'état existent (TC-D2-06)."""
    source = CSS.read_text()
    animations = re.findall(r"^\s*animation:\s*[^;]+;", source, flags=re.M)
    assert animations == [], f"animation automatique : {animations}"
    survols = re.findall(r"^[^@\n]*:hover[^{]*\{", source, flags=re.M)
    assert survols == [], f"effet au survol : {survols}"
    for gabarit in GABARITS:
        texte = gabarit.read_text()
        assert "hover:" not in texte, f"{gabarit.name} utilise un effet au survol"
        assert "animate-" not in texte, f"{gabarit.name} déclenche une animation"


# ==========================================================================
# Tics à bannir (repris de la révision précédente, non contredits par
# celle-ci) et vocabulaire imposé par la structure (grand titre, section 4).
# ==========================================================================


def test_no_trailing_arrows_and_no_middot_separators():
    fautes = []
    for gabarit in GABARITS:
        texte = gabarit.read_text()
        if "·" in texte:
            fautes.append(f"{gabarit.name} : séparateur « · »")
        if "→" in texte:
            fautes.append(f"{gabarit.name} : flèche « → »")
    assert fautes == [], fautes


def test_ac_d2_2_dashboard_hero_number_is_at_least_thirty_px():
    """AC-D2-2 : grand titre/chiffre ≥ 30 px sur l'écran de synthèse."""
    source = CSS.read_text()
    regle = re.search(r"\.heros-chiffre\s*\{([^}]*)\}", source).group(1)
    taille = int(re.search(r"font-size:\s*(\d+)px", regle).group(1))
    assert taille >= 30, f".heros-chiffre fait {taille}px, minimum 30"


def test_ac_d2_1_no_floating_white_card_class_remains_in_templates():
    """AC-D2-1 : aucun écran principal n'affiche de carte blanche flottante
    sur fond gris. La classe qui produisait ce système (`bloc`) a été
    retirée de la feuille de style ; elle ne doit plus être écrite non plus,
    sans quoi elle resterait une classe morte trompeuse dans le HTML."""
    for gabarit in GABARITS:
        classes = re.findall(r'class="([^"]*)"', gabarit.read_text())
        for attribut in classes:
            mots = attribut.split()
            assert "bloc" not in mots, f"{gabarit.name} écrit encore la classe « bloc »"


def test_ac_d2_4_quick_action_justifications_are_documented_in_the_template():
    """AC-D2-4 : chaque action de la rangée rapide porte sa justification
    écrite (fréquence ou urgence), en commentaire dans le gabarit."""
    dashboard = Path(RACINE / "app" / "templates" / "dashboard.html").read_text()
    for action, mot_cle in [
        ("Compter", "fréquence la plus haute"),
        ("Importer ventes", "flux quotidien"),
        ("Réceptions", "F1"),
        ("Commandes", "urgence"),
    ]:
        assert mot_cle in dashboard, (
            f"justification de l'action « {action} » introuvable (mot-clé "
            f"« {mot_cle} » absent du commentaire)"
        )


def test_number_input_spin_buttons_are_suppressed_for_consistency():
    """Chromium masque déjà le spinner d'un `<input type=number>` quand la
    valeur est trop large pour lui faire de la place — d'où une incohérence
    visuelle d'une ligne à l'autre du comptage. Retiré explicitement plutôt
    que laissé au hasard de la largeur de la valeur ; sans ce retrait, un
    spinner visible serait aussi une cible bien en dessous des 48 px de cet
    écran."""
    source = CSS.read_text()
    assert "-webkit-inner-spin-button" in source
    assert "-webkit-appearance: none" in source

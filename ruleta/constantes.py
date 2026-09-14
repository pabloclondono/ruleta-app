ROJO = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NEGRO = set(range(1, 37)) - ROJO

FILAS = [
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
]

VALORES_FICHAS = [50, 500, 2500, 5000, 25000, 50000]
COLOR_FICHA = {50: "#d7dce8", 500: "#c81e1e", 2500: "#1d7c1d",
               5000: "#121212", 25000: "#6a2c91", 50000: "#1b4f8a"}
TEXTO_FICHA = {50: "#1a1a1a", 500: "#ffffff", 2500: "#ffffff",
               5000: "#ffffff", 25000: "#ffffff", 50000: "#ffffff"}

# 13 corners de la estrategia "12 Corners" (C0 = 0-1-2-3, opcional)
CORNERES = {
    "C0":  (0, 1, 2, 3),
    "C1":  (1, 2, 4, 5),
    "C2":  (2, 3, 5, 6),
    "C3":  (7, 8, 10, 11),
    "C4":  (8, 9, 11, 12),
    "C5":  (13, 14, 16, 17),
    "C6":  (14, 15, 17, 18),
    "C7":  (19, 20, 22, 23),
    "C8":  (20, 21, 23, 24),
    "C9":  (25, 26, 28, 29),
    "C10": (26, 27, 29, 30),
    "C11": (31, 32, 34, 35),
    "C12": (32, 33, 35, 36),
}
_NUM_CORNERES = {}
for _cid, _nums in CORNERES.items():
    for _n in _nums:
        _NUM_CORNERES.setdefault(_n, []).append(_cid)

FONDO   = "#141414"
PANEL   = "#1e1e1e"
TEXTO   = "#e8e8e8"
SUB     = "#8f8f8f"
ORO     = "#d9a621"
VERDE   = "#166b16"
ROJO_BG = "#c81e1e"
NEGRO_BG = "#111111"
AZUL    = "#1b4f8a"
GRIS    = "#3a3a3a"

BASE_W, BASE_H = 1000, 720


def _claro(color, factor):
    from PySide6.QtGui import QColor
    c = QColor(color)
    c = c.lighter(factor)
    return c.name()


def _nom_corner(cid):
    nums = CORNERES[cid]
    return "%d-%d" % (min(nums), max(nums))


def color_numero(n):
    if n in ROJO:
        return "rojo"
    if n in NEGRO:
        return "negro"
    return "verde"
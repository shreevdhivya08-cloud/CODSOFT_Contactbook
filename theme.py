"""
Design Tokens for ContactBook UI
Centralised palette, typography, and spacing constants.
"""

# ── Palette ────────────────────────────────────────────────────────────────────
# Primary: deep indigo (trustworthy, professional)
# Accent:  vivid violet-blue (interactive elements)
# Surface: near-black / warm-white depending on mode

COLORS = {
    "dark": {
        "bg_primary":    "#0F0E17",   # near-black with a hint of blue
        "bg_secondary":  "#1C1B29",   # sidebar / card background
        "bg_tertiary":   "#252438",   # input backgrounds, table rows
        "bg_hover":      "#2D2B47",   # row hover
        "accent":        "#7C6EFA",   # primary interactive
        "accent_hover":  "#9B8FFB",
        "accent_dim":    "#4B3FBF",   # pressed / subtle
        "success":       "#4ECDC4",
        "danger":        "#FF6B6B",
        "warning":       "#FFD93D",
        "star":          "#FFD93D",   # favorite star
        "text_primary":  "#FFFFFE",
        "text_secondary":"#B2B0CC",
        "text_disabled": "#5A587A",
        "border":        "#2D2B47",
        "separator":     "#1E1D30",
        "table_header":  "#7C6EFA",
        "table_row_odd": "#1C1B29",
        "table_row_even":"#211F34",
        "table_select":  "#32305A",
    },
    "light": {
        "bg_primary":    "#F4F3FF",
        "bg_secondary":  "#FFFFFF",
        "bg_tertiary":   "#EDEEFF",
        "bg_hover":      "#E0DEFF",
        "accent":        "#5548E0",
        "accent_hover":  "#7C6EFA",
        "accent_dim":    "#C5C0FA",
        "success":       "#2BAE9A",
        "danger":        "#E03E3E",
        "warning":       "#C88F00",
        "star":          "#C88F00",
        "text_primary":  "#0F0E17",
        "text_secondary":"#4A4870",
        "text_disabled": "#ABACC0",
        "border":        "#D8D6F0",
        "separator":     "#E8E7FA",
        "table_header":  "#5548E0",
        "table_row_odd": "#FFFFFF",
        "table_row_even":"#F4F3FF",
        "table_select":  "#E0DEFF",
    },
}

# ── Typography ─────────────────────────────────────────────────────────────────
FONTS = {
    "app_title":    ("Segoe UI", 22, "bold"),
    "section":      ("Segoe UI", 13, "bold"),
    "body":         ("Segoe UI", 12),
    "body_bold":    ("Segoe UI", 12, "bold"),
    "small":        ("Segoe UI", 11),
    "small_bold":   ("Segoe UI", 11, "bold"),
    "micro":        ("Segoe UI", 10),
    "input":        ("Segoe UI", 12),
    "table_header": ("Segoe UI", 11, "bold"),
    "table_body":   ("Segoe UI", 11),
    "stat_number":  ("Segoe UI", 26, "bold"),
    "stat_label":   ("Segoe UI", 10),
    "nav":          ("Segoe UI", 12, "bold"),
}

# ── Spacing / sizing ───────────────────────────────────────────────────────────
SIDEBAR_WIDTH   = 200
DETAIL_WIDTH    = 310
ROW_HEIGHT      = 36
CORNER_RADIUS   = 10
PAD             = 12

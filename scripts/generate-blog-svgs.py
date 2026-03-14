#!/usr/bin/env python3
"""Generate Gruvbox-themed terminal SVG images for blog posts."""

import os
import html

# Gruvbox Dark palette
COLORS = {
    'bg': '#282828',
    'bg_dark': '#1d2021',
    'fg': '#ebdbb2',
    'fg_dim': '#928374',
    'red': '#fb4934',
    'green': '#b8bb26',
    'yellow': '#fabd2f',
    'blue': '#83a598',
    'purple': '#d3869b',
    'aqua': '#8ec07c',
    'orange': '#fe8019',
    'separator': '#504945',
}

FONT_SIZE = 12
LINE_HEIGHT = 18
CHAR_WIDTH = 7.2  # approximate for monospace at 12px
TITLE_BAR_HEIGHT = 32
PADDING_TOP = 50
PADDING_LEFT = 20
PADDING_BOTTOM = 20


def escape(text):
    return html.escape(text)


class TerminalSVG:
    """Builder for Gruvbox terminal SVG."""

    def __init__(self, title="Terminal", width=1000):
        self.title = title
        self.width = width
        self.lines = []  # list of (y_offset, elements)
        self.y = PADDING_TOP

    def add_blank(self, count=1):
        self.y += LINE_HEIGHT * count

    def add_text(self, text, color='fg', bold=False, x=None):
        """Add a single line of text."""
        if x is None:
            x = PADDING_LEFT
        weight = ' font-weight="700"' if bold else ''
        self.lines.append(
            f'  <text x="{x}" y="{self.y}" fill="{COLORS[color]}" font-size="{FONT_SIZE}"{weight}>{escape(text)}</text>'
        )
        self.y += LINE_HEIGHT

    def add_colored_spans(self, spans, y_override=None):
        """Add a line with mixed colors: [(text, color, bold), ...]"""
        y = y_override if y_override else self.y
        x = PADDING_LEFT
        parts = []
        for span in spans:
            text, color, bold = span if len(span) == 3 else (span[0], span[1], False)
            weight = ' font-weight="700"' if bold else ''
            parts.append(
                f'<tspan x="{x}" fill="{COLORS[color]}"{weight}>{escape(text)}</tspan>'
            )
            x += len(text) * CHAR_WIDTH
        self.lines.append(f'  <text y="{y}" font-size="{FONT_SIZE}">{"".join(parts)}</text>')
        if y_override is None:
            self.y += LINE_HEIGHT

    def add_separator(self, x1=None, x2=None):
        if x1 is None:
            x1 = PADDING_LEFT
        if x2 is None:
            x2 = self.width - PADDING_LEFT
        # Place line just below the previous text baseline (y was already incremented)
        line_y = self.y - LINE_HEIGHT + 5
        self.lines.append(
            f'  <line x1="{x1}" y1="{line_y}" x2="{x2}" y2="{line_y}" stroke="{COLORS["separator"]}" stroke-width="1"/>'
        )
        self.y += 4  # small gap after separator

    def add_table_row(self, cells, col_widths):
        """cells: [(text, color, bold), ...], col_widths: [int, ...]"""
        x = PADDING_LEFT
        parts = []
        for i, cell in enumerate(cells):
            text, color, bold = cell if len(cell) == 3 else (cell[0], cell[1], False)
            weight = ' font-weight="700"' if bold else ''
            parts.append(
                f'<tspan x="{x}" fill="{COLORS[color]}"{weight}>{escape(text)}</tspan>'
            )
            x += col_widths[i] if i < len(col_widths) else 60
        self.lines.append(f'  <text y="{self.y}" font-size="{FONT_SIZE}">{"".join(parts)}</text>')
        self.y += LINE_HEIGHT

    def add_command(self, cmd, prompt="❯"):
        """Add a command prompt line."""
        self.add_colored_spans([
            (prompt + " ", 'green'),
            (cmd, 'fg'),
        ])

    def render(self):
        height = self.y + PADDING_BOTTOM
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}">',
            '  <defs>',
            "    <style>",
            "      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');",
            "      text { font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace; }",
            '    </style>',
            '  </defs>',
            '',
            f'  <!-- Terminal background -->',
            f'  <rect width="{self.width}" height="{height}" rx="10" fill="{COLORS["bg"]}"/>',
            '',
            f'  <!-- Title bar -->',
            f'  <rect width="{self.width}" height="{TITLE_BAR_HEIGHT}" rx="10" fill="{COLORS["bg_dark"]}"/>',
            f'  <rect y="22" width="{self.width}" height="10" fill="{COLORS["bg_dark"]}"/>',
            f'  <circle cx="20" cy="16" r="6" fill="#cc241d"/>',
            f'  <circle cx="40" cy="16" r="6" fill="#d79921"/>',
            f'  <circle cx="60" cy="16" r="6" fill="#98971a"/>',
            f'  <text x="{self.width // 2}" y="20" text-anchor="middle" fill="{COLORS["fg_dim"]}" font-size="12">{escape(self.title)}</text>',
            '',
        ]
        svg_parts.extend(self.lines)
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.render())
        print(f"  Generated: {path}")


def make_score_color(val, thresholds=None):
    """Return color based on score value."""
    if thresholds is None:
        thresholds = {'high': 80, 'mid': 60, 'senior': 40, 'low': 20}
    try:
        v = float(val)
    except (ValueError, TypeError):
        return 'fg_dim'
    if v >= thresholds['high']:
        return 'purple'
    elif v >= thresholds['mid']:
        return 'green'
    elif v >= thresholds['senior']:
        return 'yellow'
    elif v >= thresholds['low']:
        return 'fg'
    else:
        return 'fg_dim'


def total_color(val):
    try:
        v = float(val)
    except (ValueError, TypeError):
        return 'fg_dim'
    if v >= 80:
        return 'purple'
    elif v >= 60:
        return 'green'
    elif v >= 40:
        return 'yellow'
    else:
        return 'fg'


def role_color(role):
    if 'Architect' in role:
        return 'purple'
    elif 'Anchor' in role:
        return 'blue'
    elif 'Producer' in role:
        return 'yellow'
    elif 'Cleaner' in role:
        return 'aqua'
    return 'fg_dim'


def state_color(state):
    if 'Active' in state:
        return 'green'
    elif 'Growing' in state:
        return 'blue'
    elif 'Former' in state:
        return 'fg_dim'
    elif 'Fragile' in state:
        return 'red'
    elif 'Silent' in state:
        return 'fg_dim'
    return 'fg'


# ─── Code Card SVG (non-terminal style) ───

CARD_FONT_SIZE = 14
CARD_LINE_HEIGHT = 22
CARD_CODE_FONT_SIZE = 12
CARD_CODE_LINE_HEIGHT = 18
CARD_PADDING_LEFT = 24
CARD_PADDING_TOP = 28
CARD_PADDING_BOTTOM = 20
CARD_ACCENT_WIDTH = 4

# Accent colors by type
ACCENT_COLORS = {
    'formula': '#8ec07c',   # aqua
    'python': '#b8bb26',    # green
    'yaml': '#fabd2f',      # yellow
    'bash': '#fe8019',      # orange
    'diagram': '#83a598',   # blue
    'data': '#d3869b',      # purple
}


class CodeCardSVG:
    """Builder for Gruvbox code card SVG (no terminal chrome)."""

    def __init__(self, card_type='formula', width=720, label=None):
        self.card_type = card_type
        self.width = width
        self.label = label or card_type.capitalize()
        self.accent = ACCENT_COLORS.get(card_type, COLORS['aqua'])
        self.lines = []
        self.y = CARD_PADDING_TOP
        self._font_size = CARD_FONT_SIZE if card_type == 'formula' else CARD_CODE_FONT_SIZE
        self._line_height = CARD_LINE_HEIGHT if card_type == 'formula' else CARD_CODE_LINE_HEIGHT

    def add_line(self, text, color='fg', bold=False):
        weight = ' font-weight="700"' if bold else ''
        self.lines.append(
            f'  <text x="{CARD_PADDING_LEFT}" y="{self.y}" fill="{COLORS[color]}" '
            f'font-size="{self._font_size}"{weight}>{escape(text)}</text>'
        )
        self.y += self._line_height

    def add_spans(self, spans):
        """Add a line with mixed colors: [(text, color, bold?), ...]"""
        x = CARD_PADDING_LEFT
        parts = []
        cw = self._font_size * 0.6  # char width approx
        for span in spans:
            text, color = span[0], span[1]
            bold = span[2] if len(span) > 2 else False
            weight = ' font-weight="700"' if bold else ''
            parts.append(
                f'<tspan x="{x}" fill="{COLORS[color]}"{weight}>{escape(text)}</tspan>'
            )
            x += len(text) * cw
        self.lines.append(f'  <text y="{self.y}" font-size="{self._font_size}">{"".join(parts)}</text>')
        self.y += self._line_height

    def add_blank(self, count=1):
        self.y += self._line_height * count

    def add_separator(self):
        line_y = self.y - self._line_height + 5
        self.lines.append(
            f'  <line x1="{CARD_PADDING_LEFT}" y1="{line_y}" x2="{self.width - 20}" y2="{line_y}" '
            f'stroke="{COLORS["separator"]}" stroke-width="1"/>'
        )
        self.y += 4

    def render(self):
        height = self.y + CARD_PADDING_BOTTOM
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}">',
            '  <defs>',
            "    <style>",
            "      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');",
            "      text { font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace; }",
            '    </style>',
            '  </defs>',
            '',
            f'  <!-- Card background -->',
            f'  <rect width="{self.width}" height="{height}" rx="8" fill="{COLORS["bg_dark"]}"/>',
            '',
            f'  <!-- Accent bar -->',
            f'  <rect x="0" y="0" width="{CARD_ACCENT_WIDTH}" height="{height}" rx="2" fill="{self.accent}"/>',
            '',
            f'  <!-- Category label -->',
            f'  <text x="{self.width - 28}" y="18" text-anchor="end" fill="{COLORS["separator"]}" font-size="10">{escape(self.label)}</text>',
            '',
        ]
        svg_parts.extend(self.lines)
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.render())
        print(f"  Generated: {path}")


# ─── IMAGE OUTPUT DIRECTORY ───
IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'images', 'blog')
os.makedirs(IMG_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════
# CHAPTER 1 — Individual Scoring
# ════════════════════════════════════════════════════════════

def ch1_backend_table():
    svg = TerminalSVG("Terminal — eis analyze --recursive ~/workspace", width=1180)
    svg.add_command("eis analyze --config eis.yaml --recursive ~/workspace")
    svg.add_blank()
    svg.add_text("═══ Backend ═══", color='red', bold=True)
    svg.add_text("Analyzed 12 repo(s), 10 engineers", color='fg_dim')
    svg.add_blank()

    #                #   Member Active Prod Qual Robust Dorm Design Brdth Debt Indisp Grav Total     Role       Style      State
    cols = [28, 120, 55, 46, 46, 58, 55, 58, 52, 46, 52, 48, 100, 140, 132, 110]
    headers = ['#', 'Member', 'Active', 'Prod', 'Qual', 'Robust', 'Dormnt', 'Design', 'Brdth', 'Debt', 'Indisp', 'Grav', 'Total', 'Role', 'Style', 'State']
    svg.add_table_row([(h, 'aqua', True) for h in headers], cols)
    svg.add_separator()

    rows = [
        ('1', 'machuz', '✓', '100', '57', '100', '100', '100', '74', '100', '43', '97', '90.3', 'Architect (1.00)', 'Builder (1.00)', 'Active'),
        ('2', 'Engineer F', '—', '69', '73', '12', '67', '81', '81', '11', '100', '52', '52.8', 'Architect (0.88)', '—', 'Former'),
        ('3', 'Engineer G', '✓', '17', '69', '50', '14', '48', '48', '88', '35', '44', '44.5', 'Anchor (0.96)', 'Balanced (0.30)', 'Active'),
        ('4', 'Engineer H', '✓', '27', '84', '30', '28', '52', '52', '71', '8', '41', '41.8', 'Anchor (0.98)', 'Balanced (0.30)', 'Active'),
        ('5', 'Engineer X', '—', '6', '79', '0', '4', '78', '78', '50', '0', '24', '24.9', '—', 'Spread (1.00)', 'Former'),
    ]

    for r in rows:
        rank, name, active, prod, qual, robust, dormant, design, breadth, debt, indisp, grav, total_str, role_str, style, state = r
        cells = [
            (rank, 'fg'),
            (name, 'yellow'),
            (active, 'green' if active == '✓' else 'fg_dim'),
            (prod, make_score_color(prod)),
            (qual, make_score_color(qual)),
            (robust, make_score_color(robust)),
            (dormant, make_score_color(dormant)),
            (design, make_score_color(design)),
            (breadth, make_score_color(breadth)),
            (debt, make_score_color(debt)),
            (indisp, make_score_color(indisp)),
            (grav, make_score_color(grav)),
            (total_str, total_color(total_str), True),
            (role_str, role_color(role_str)),
            (style, 'blue' if style != '—' else 'fg_dim'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)

    svg.save(os.path.join(IMG_DIR, 'ch1-backend-table.svg'))


def ch1_frontend_table():
    svg = TerminalSVG("Terminal — eis analyze (Frontend)", width=1180)
    svg.add_text("═══ Frontend ═══", color='red', bold=True)
    svg.add_text("Analyzed 8 repo(s), 8 engineers", color='fg_dim')
    svg.add_blank()

    cols = [25, 110, 50, 42, 42, 52, 50, 52, 48, 42, 48, 42, 50, 135, 125, 100]
    headers = ['#', 'Member', 'Active', 'Prod', 'Qual', 'Robust', 'Dormnt', 'Design', 'Brdth', 'Debt', 'Indisp', 'Grav', 'Total', 'Role', 'Style', 'State']
    svg.add_table_row([(h, 'aqua', True) for h in headers], cols)
    svg.add_separator()

    rows = [
        ('1', 'Engineer D', '✓', '100', '84', '100', '100', '100', '62', '39', '100', '84', '85.4', 'Architect (1.00)', 'Builder (1.00)', 'Active'),
        ('—', 'Engineer Y', '—', '24', '18', '0', '17', '38', '38', '0', '0', '12', '12.6', 'Producer (0.68)', 'Mass (0.81)', 'Former'),
    ]

    for r in rows:
        rank, name, active, prod, qual, robust, dormant, design, breadth, debt, indisp, grav, total_str, role_str, style, state = r
        cells = [
            (rank, 'fg'),
            (name, 'yellow'),
            (active, 'green' if active == '✓' else 'fg_dim'),
            (prod, make_score_color(prod)),
            (qual, make_score_color(qual)),
            (robust, make_score_color(robust)),
            (dormant, make_score_color(dormant)),
            (design, make_score_color(design)),
            (breadth, make_score_color(breadth)),
            (debt, make_score_color(debt)),
            (indisp, make_score_color(indisp)),
            (grav, make_score_color(grav)),
            (total_str, total_color(total_str), True),
            (role_str, role_color(role_str)),
            (style, 'blue' if style not in ('—', '') else 'fg_dim'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)

    svg.save(os.path.join(IMG_DIR, 'ch1-frontend-table.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 2 — Team Health
# ════════════════════════════════════════════════════════════

def ch2_warnings():
    svg = TerminalSVG("Terminal — eis team --recursive ~/workspace", width=900)
    svg.add_command("eis team --recursive ~/workspace")
    svg.add_blank()
    svg.add_text("═══ Backend (4 core + 3 risk / 12 total, 13 repos) ═══", color='red', bold=True)
    svg.add_blank()
    svg.add_text("⚠ Warnings:", color='orange', bold=True)
    svg.add_text("  43% risk ratio — 3 of 7 effective members are Former/Silent/Fragile", color='orange')
    svg.add_text("  Top contributor (machuz) accounts for 46% of core production", color='orange')
    svg.add_text("  — ProdDensity drops to 39 without them", color='orange')
    svg.add_text("  2 Silent members — headcount says 16 but effective contributors are 4", color='orange')
    svg.add_text("  Fragile gravity — okatechnology (Grav 68) has high influence", color='orange')
    svg.add_text("    but low robust survival (8)", color='orange')
    svg.save(os.path.join(IMG_DIR, 'ch2-warnings.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 3 — Archetypes
# ════════════════════════════════════════════════════════════

def ch3_engineer_profiles():
    svg = TerminalSVG("Terminal — Engineer Archetypes", width=900)

    profiles = [
        ("Engineer A — The Builder Architect", "purple",
         "Prod 100 | Qual 84 | Robust 100 | Dormant 100 | Design 100 | Grav 84 | Total 88.9",
         "Role: Architect (1.00) | Style: Builder (1.00)"),
        ("Engineer B — The Mass Anchor", "blue",
         "Prod 100 | Qual 87 | Robust 11 | Dormant 18 | Design 39 | Grav 32 | Total 44.6",
         "Role: Anchor (1.00) | Style: Mass (0.81)"),
        ("Engineer C — The Balanced Producer", "yellow",
         "Prod 42 | Qual 44 | Robust 39 | Dormant 39 | Design 9 | Grav 29 | Total 39.5",
         "Role: Producer (0.80) | Style: Balanced (0.30)"),
        ("Engineer D — The Emergent Producer", "yellow",
         "Prod 49 | Qual 66 | Robust 12 | Dormant 44 | Design 5 | Grav 68 | Indisp 100 | Total 39.0",
         "Role: Producer (0.96) | Style: Emergent (0.78)"),
        ("Engineer E — The Churn Producer", "orange",
         "Prod 37 | Qual 23 | Robust 10 | Dormant 2 | Design 2 | Grav 35 | Total 19.2",
         "Role: Producer (0.68) | Style: Churn (0.67)"),
    ]

    for name, color, scores, role in profiles:
        svg.add_text(name, color=color, bold=True)
        svg.add_text(f"  {scores}", color='fg')
        svg.add_text(f"  {role}", color='blue')
        svg.add_blank()

    svg.save(os.path.join(IMG_DIR, 'ch3-engineer-profiles.svg'))


def ch3_producer_warning():
    svg = TerminalSVG("Terminal — Team Warning", width=500)
    svg.add_text("Role Distribution:", color='aqua', bold=True)
    svg.add_colored_spans([
        ("  Producer     ", 'yellow'),
        ("██████████", 'yellow'),
        ("  5 (100%)", 'fg_dim'),
    ])
    svg.save(os.path.join(IMG_DIR, 'ch3-producer-warning.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 4 — Backend Architect Concentration
# ════════════════════════════════════════════════════════════

def ch4_backend_team():
    svg = TerminalSVG("Terminal — eis analyze (Backend)", width=1250)
    svg.add_text("═══ Backend ═══", color='red', bold=True)
    svg.add_text("Analyzed 13 repo(s), 12 engineers", color='fg_dim')
    svg.add_blank()

    #                #  Member Active Prod Qual Robust Dorm Design Grav Total     Role       Style       State
    cols = [28, 120, 55, 46, 46, 58, 55, 58, 48, 100, 145, 140, 125]
    headers = ['#', 'Member', 'Active', 'Prod', 'Qual', 'Robust', 'Dormnt', 'Design', 'Grav', 'Total', 'Role', 'Style', 'State']
    svg.add_table_row([(h, 'aqua', True) for h in headers], cols)
    svg.add_separator()

    rows = [
        ('1', 'machuz', '✓', '100', '66', '100', '100', '100', '97', '92.4', 'Architect (1.00)', 'Builder (1.00)', 'Active (0.80)'),
        ('2', 'Engineer F', '—', '93', '75', '36', '21', '47', '76', '55.5', 'Anchor (0.87)', 'Resilient (0.66)', 'Former (0.73)'),
        ('3', 'Engineer G', '✓', '52', '78', '21', '32', '12', '26', '37.3', 'Anchor (0.96)', 'Balanced (0.30)', 'Active (0.80)'),
        ('4', 'Engineer H', '✓', '49', '90', '20', '25', '10', '31', '35.6', 'Anchor (0.98)', 'Balanced (0.30)', 'Active (0.80)'),
    ]

    for r in rows:
        rank, name, active, prod, qual, robust, dormant, design, grav, total_str, role_str, style, state = r
        cells = [
            (rank, 'fg'),
            (name, 'yellow'),
            (active, 'green' if active == '✓' else 'fg_dim'),
            (prod, make_score_color(prod)),
            (qual, make_score_color(qual)),
            (robust, make_score_color(robust)),
            (dormant, make_score_color(dormant)),
            (design, make_score_color(design)),
            (grav, make_score_color(grav)),
            (total_str, total_color(total_str), True),
            (role_str, role_color(role_str)),
            (style, 'blue'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)

    svg.save(os.path.join(IMG_DIR, 'ch4-backend-team.svg'))


def ch4_team_classification():
    svg = TerminalSVG("Terminal — eis team (Backend)", width=700)
    svg.add_text("═══ Backend (4 core + 3 risk / 12 total, 13 repos) ═══", color='red', bold=True)
    svg.add_text("  ★ Elite (1.00)", color='yellow', bold=True)
    svg.add_blank()
    svg.add_text("Classification:", color='aqua', bold=True)
    svg.add_text("  Structure: Emerging Architecture (0.66)", color='fg')
    svg.add_text("  Phase:     Legacy-Heavy (0.67)", color='fg')
    svg.add_text("  Risk:      Talent Drain (0.43)", color='orange')
    svg.add_blank()
    svg.add_text("Role Distribution:", color='aqua', bold=True)
    svg.add_colored_spans([("  Architect    ", 'purple'), ("█░░░░░░░░░", 'purple'), ("  1 (14%)", 'fg_dim')])
    svg.add_colored_spans([("  Anchor       ", 'blue'), ("████░░░░░░", 'blue'), ("  3 (43%)", 'fg_dim')])
    svg.add_colored_spans([("  —            ", 'fg_dim'), ("████░░░░░░", 'fg_dim'), ("  3 (43%)", 'fg_dim')])
    svg.save(os.path.join(IMG_DIR, 'ch4-team-classification.svg'))


def ch4_structure():
    svg = TerminalSVG("Backend Team Structure", width=400)
    svg.add_text("Star (Architect)", color='purple', bold=True)
    svg.add_text("    ↓", color='fg_dim')
    svg.add_text("  Planets (Anchors)", color='blue', bold=True)
    svg.add_text("    ↓", color='fg_dim')
    svg.add_text("  Vacuum (No Producers)", color='red', bold=True)
    svg.save(os.path.join(IMG_DIR, 'ch4-structure.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 5 — Timeline
# ════════════════════════════════════════════════════════════

def _timeline_table(svg, name, domain, rows):
    """Helper for timeline table generation."""
    svg.add_text(f"--- {name} ({domain}) ---", color='yellow', bold=True)
    cols = [140, 55, 50, 50, 50, 60, 130, 130, 120]
    headers = ['Period', 'Total', 'Prod', 'Qual', 'Surv', 'Design', 'Role', 'Style', 'State']
    svg.add_table_row([(h, 'aqua', True) for h in headers], cols)
    svg.add_separator()

    for r in rows:
        period, total, prod, qual, surv, design = r[:6]
        role = r[6] if len(r) > 6 else ''
        style = r[7] if len(r) > 7 else ''
        state = r[8] if len(r) > 8 else ''
        cells = [
            (period, 'fg_dim'),
            (total, total_color(total), True),
            (prod, make_score_color(prod)),
            (qual, make_score_color(qual)),
            (surv, make_score_color(surv)),
            (design, make_score_color(design)),
            (role, role_color(role)),
            (style, 'blue' if style and style != '—' else 'fg_dim'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)


def ch5_engineer_f_timeline():
    svg = TerminalSVG("Terminal — eis timeline (Engineer F, Backend)", width=950)
    svg.add_command("eis timeline --author engineer-f --recursive ~/workspace")
    svg.add_blank()

    rows = [
        ('2024-Q1 (Jan)', '90.0', '100', '69', '100', '100', 'Architect', 'Builder', ''),
        ('2024-Q2 (Apr)', '94.4', '100', '71', '100', '87', 'Architect', 'Builder', ''),
        ('2024-Q3 (Jul)', '72.5', '59', '72', '100', '71', 'Producer', 'Balanced', ''),
        ('2024-Q4 (Oct)', '90.6', '100', '77', '100', '100', 'Architect', 'Builder', ''),
        ('2025-Q1 (Jan)', '79.2', '100', '82', '100', '28', 'Anchor', 'Balanced', ''),
        ('2025-Q2 (Apr)', '68.4', '36', '84', '100', '58', 'Anchor', 'Balanced', ''),
        ('2025-Q3 (Jul)', '49.1', '81', '77', '51', '4', 'Anchor', 'Balanced', ''),
        ('2025-Q4 (Oct)', '31.2', '18', '78', '23', '8', '—', 'Balanced', 'Fragile'),
        ('2026-Q1 (Jan)', '11.3', '0', '0', '34', '0', '—', '—', 'Former'),
    ]
    _timeline_table(svg, "Engineer F", "Backend", rows)
    svg.save(os.path.join(IMG_DIR, 'ch5-engineer-f-timeline.svg'))


def ch5_engineer_j_timeline():
    svg = TerminalSVG("Terminal — eis timeline (Engineer J, Frontend)", width=950)
    rows = [
        ('2024-Q1 (Jan)', '28.1', '26', '73', '33', '2', 'Anchor', '—', 'Growing'),
        ('2024-Q2 (Apr)', '15.5', '8', '100', '16', '0', '—', '—', 'Growing'),
        ('2024-Q3 (Jul)', '61.9', '52', '72', '38', '100', 'Architect', 'Balanced', ''),
        ('2024-Q4 (Oct)', '91.7', '100', '74', '96', '100', 'Architect', 'Builder', ''),
        ('2025-Q1 (Jan)', '63.9', '90', '85', '15', '61', 'Anchor', 'Emergent', ''),
        ('2025-Q2 (Apr)', '63.8', '48', '73', '76', '81', 'Architect', 'Balanced', ''),
        ('2025-Q3 (Jul)', '44.7', '62', '70', '18', '18', 'Producer', 'Emergent', ''),
        ('2025-Q4 (Oct)', '39.4', '62', '60', '50', '0', 'Producer', 'Balanced', 'Former'),
        ('2026-Q1 (Jan)', '54.2', '43', '61', '100', '1', 'Producer', 'Balanced', 'Active'),
    ]
    _timeline_table(svg, "Engineer J", "Frontend", rows)
    svg.save(os.path.join(IMG_DIR, 'ch5-engineer-j-timeline.svg'))


def ch5_engineer_i_timeline():
    svg = TerminalSVG("Terminal — eis timeline (Engineer I, Frontend)", width=950)
    rows = [
        ('2024-Q3 (Jul)', '56.1', '100', '97', '60', '2', 'Anchor', 'Balanced', ''),
        ('2024-Q4 (Oct)', '75.7', '59', '84', '100', '78', 'Architect', 'Balanced', ''),
        ('2025-Q1 (Jan)', '87.5', '100', '93', '100', '100', 'Architect', 'Builder', ''),
        ('2025-Q2 (Apr)', '73.2', '67', '91', '100', '100', 'Architect', 'Builder', ''),
        ('2025-Q3 (Jul)', '72.4', '73', '97', '100', '73', 'Anchor', 'Balanced', ''),
        ('2025-Q4 (Oct)', '81.7', '100', '68', '100', '100', 'Architect', 'Balanced', ''),
        ('2026-Q1 (Jan)', '78.1', '100', '84', '83', '100', 'Anchor', 'Builder', 'Active'),
    ]
    _timeline_table(svg, "Engineer I", "Frontend", rows)
    svg.save(os.path.join(IMG_DIR, 'ch5-engineer-i-timeline.svg'))


def ch5_per_repo_commits():
    svg = TerminalSVG("Per-Repository Commit Distribution — Engineer I", width=700)
    cols = [120, 160, 160, 160]
    svg.add_table_row([('Quarter', 'aqua', True), ('Repo A (existing)', 'aqua', True), ('Repo B (existing)', 'aqua', True), ('Repo C (new)', 'aqua', True)], cols)
    svg.add_separator()
    svg.add_table_row([('2025-Q2', 'fg_dim'), ('135', 'fg'), ('44', 'fg'), ('—', 'fg_dim')], cols)
    svg.add_table_row([('2025-Q3', 'fg_dim'), ('201', 'fg'), ('274', 'fg'), ('—', 'fg_dim')], cols)
    svg.add_table_row([('2025-Q4', 'fg_dim'), ('5', 'fg_dim'), ('5', 'fg_dim'), ('1,352', 'purple', True)], cols)
    svg.add_table_row([('2026-Q1', 'fg_dim'), ('2', 'fg_dim'), ('2', 'fg_dim'), ('1,333', 'purple', True)], cols)
    svg.save(os.path.join(IMG_DIR, 'ch5-per-repo-commits.svg'))


def ch5_transitions():
    svg = TerminalSVG("Terminal — Notable Transitions", width=800)
    svg.add_text("Notable transitions:", color='aqua', bold=True)
    transitions_i = [
        ("  * Engineer I: Role ", "Anchor", "→", "Architect", " (2024-Q4)", ""),
        ("  * Engineer I: Style ", "Balanced", "→", "Builder", " (2025-Q1)", ""),
        ("  * Engineer I: Role ", "Architect", "→", "Anchor", " (2025-Q3)", "  ← friction"),
        ("  * Engineer I: Style ", "Builder", "→", "Balanced", " (2025-Q3)", "  ← hesitation"),
        ("  * Engineer I: Role ", "Anchor", "→", "Architect", " (2025-Q4)", "  ← return"),
    ]
    for t in transitions_i:
        svg.add_colored_spans([
            (t[0], 'fg'),
            (t[1], 'blue'),
            (t[2], 'fg_dim'),
            (t[3], role_color(t[3])),
            (t[4], 'fg_dim'),
            (t[5], 'red') if t[5] else (t[5], 'fg'),
        ])

    svg.add_blank()
    transitions_j = [
        ("  * Engineer J: Style ", "Balanced", "→", "Builder", " (2024-Q4)", "  ← building phase"),
        ("  * Engineer J: Role ", "Architect", "→", "Producer", " (2025-Q3)", "  ← structure complete"),
        ("  * Engineer J: State ", "Former", "→", "Active", " (2026-Q1)", "  ← return"),
    ]
    for t in transitions_j:
        svg.add_colored_spans([
            (t[0], 'fg'),
            (t[1], 'blue'),
            (t[2], 'fg_dim'),
            (t[3], role_color(t[3]) if 'Role' in t[0] else state_color(t[3]) if 'State' in t[0] else 'blue'),
            (t[4], 'fg_dim'),
            (t[5], 'green') if 'return' in t[5] else (t[5], 'aqua'),
        ])

    svg.save(os.path.join(IMG_DIR, 'ch5-transitions.svg'))


def ch5_comparison_table():
    svg = TerminalSVG("Timeline Comparison — Engineer F vs machuz (Backend)", width=900)

    cols = [120, 60, 140, 30, 60, 140]
    svg.add_table_row([
        ('', 'fg'), ('', 'fg'),
        ('Engineer F (BE)', 'yellow', True),
        ('', 'fg'), ('', 'fg'),
        ('machuz (BE)', 'yellow', True),
    ], cols)
    svg.add_separator()

    rows = [
        ('2024-Q1', '90.0', 'Architect Builder', '', '--', ''),
        ('2024-Q2', '94.4', 'Architect Builder', '', '31.5', 'Anchor Balanced'),
        ('2024-Q3', '72.5', 'Producer Balanced', '', '73.8', 'Anchor Builder'),
        ('2024-Q4', '90.6', 'Architect Builder', '', '64.1', 'Anchor Builder'),
        ('2025-Q1', '79.2', 'Anchor Balanced', '', '61.7', 'Anchor Builder'),
        ('2025-Q2', '68.4', 'Anchor Balanced', '', '49.2', 'Anchor Balanced'),
        ('2025-Q3', '49.1', 'Anchor Balanced', '', '93.2', 'Architect Builder'),
        ('2025-Q4', '31.2', '— Fragile', '', '87.7', 'Architect Builder'),
        ('2026-Q1', '11.3', '— Former', '', '92.4', 'Architect Builder'),
    ]
    for r in rows:
        period, f_total, f_role, _, m_total, m_role = r
        cells = [
            (period, 'fg_dim'),
            (f_total, total_color(f_total), True),
            (f_role, role_color(f_role) if 'Architect' in f_role or 'Anchor' in f_role or 'Producer' in f_role else 'red' if 'Fragile' in f_role or 'Former' in f_role else 'fg_dim'),
            ('  ', 'fg'),
            (m_total if m_total != '--' else '—', total_color(m_total) if m_total != '--' else 'fg_dim', True),
            (m_role, role_color(m_role) if m_role else 'fg_dim'),
        ]
        svg.add_table_row(cells, cols)

    svg.save(os.path.join(IMG_DIR, 'ch5-comparison-table.svg'))


def ch5_team_timeline():
    svg = TerminalSVG("Terminal — eis timeline --team (Backend)", width=800)
    svg.add_text("=== Backend / Backend -- Team Timeline ===", color='red', bold=True)
    svg.add_blank()
    svg.add_text("Classification:", color='aqua', bold=True)

    cols = [140, 160, 160, 170]
    svg.add_table_row([('Period', 'fg_dim'), ('2024-Q4', 'fg_dim'), ('2025-Q4', 'fg_dim'), ('2026-Q1', 'fg_dim')], cols)
    svg.add_table_row([('Character', 'fg'), ('Guardian', 'blue'), ('Balanced', 'green'), ('Elite', 'yellow', True)], cols)
    svg.add_table_row([('Structure', 'fg'), ('Maintenance', 'fg_dim'), ('Unstructured', 'red'), ('Architectural Engine', 'purple', True)], cols)
    svg.add_table_row([('Phase', 'fg'), ('Declining', 'red'), ('Declining', 'red'), ('Mature', 'green')], cols)
    svg.add_table_row([('Risk', 'fg'), ('Quality Drift', 'orange'), ('Design Vacuum', 'red'), ('Healthy', 'green')], cols)
    svg.save(os.path.join(IMG_DIR, 'ch5-team-timeline.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 6 — Team Evolution
# ════════════════════════════════════════════════════════════

def ch6_backend_team_timeline():
    svg = TerminalSVG("Terminal — Backend Team Timeline", width=700)
    svg.add_text("═══ Backend — Team Timeline ═══", color='red', bold=True)
    svg.add_blank()
    svg.add_text("Classification:", color='aqua', bold=True)
    cols = [140, 180, 200]
    svg.add_table_row([('Period', 'fg_dim'), ('2024-H2', 'fg_dim'), ('2026-H1', 'fg_dim')], cols)
    svg.add_table_row([('Character', 'fg'), ('Balanced', 'green'), ('Elite', 'yellow', True)], cols)
    svg.add_table_row([('Structure', 'fg'), ('Unstructured', 'red'), ('Architectural Engine', 'purple', True)], cols)
    svg.add_table_row([('Culture', 'fg'), ('Stability', 'blue'), ('Builder', 'green')], cols)
    svg.add_table_row([('Phase', 'fg'), ('Declining', 'red'), ('Mature', 'green')], cols)
    svg.add_table_row([('Risk', 'fg'), ('Design Vacuum', 'red'), ('Healthy', 'green')], cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-backend-team-timeline.svg'))


def ch6_backend_score_averages():
    svg = TerminalSVG("Backend Score Averages", width=500)
    svg.add_text("Score Averages:", color='aqua', bold=True)
    cols = [140, 130, 130]
    svg.add_table_row([('Period', 'fg_dim'), ('2024-H2', 'fg_dim'), ('2026-H1', 'fg_dim')], cols)
    svg.add_separator()
    svg.add_table_row([('Production', 'fg'), ('0.0', 'fg_dim'), ('57.7', 'green')], cols)
    svg.add_table_row([('Quality', 'fg'), ('0.0', 'fg_dim'), ('64.6', 'green')], cols)
    svg.add_table_row([('Survival', 'fg'), ('0.0', 'fg_dim'), ('39.2', 'yellow')], cols)
    svg.add_table_row([('Design', 'fg'), ('0.0', 'fg_dim'), ('36.4', 'yellow')], cols)
    svg.add_table_row([('Total', 'fg', True), ('0.0', 'fg_dim'), ('48.3', 'yellow', True)], cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-backend-scores.svg'))


def ch6_frontend_team_timeline():
    svg = TerminalSVG("Terminal — Frontend Team Timeline", width=900)
    svg.add_text("═══ Frontend — Team Timeline ═══", color='red', bold=True)
    svg.add_blank()
    svg.add_text("Classification:", color='aqua', bold=True)
    cols = [120, 150, 140, 150, 160]
    svg.add_table_row([('Period', 'fg_dim'), ('2024-H2', 'fg_dim'), ('2025-H1', 'fg_dim'), ('2025-H2', 'fg_dim'), ('2026-H1', 'fg_dim')], cols)
    svg.add_table_row([('Character', 'fg'), ('Guardian', 'blue'), ('Factory', 'yellow'), ('Guardian', 'blue'), ('Balanced', 'green')], cols)
    svg.add_table_row([('Structure', 'fg'), ('Maintenance', 'fg_dim'), ('Delivery', 'yellow'), ('Maintenance', 'fg_dim'), ('Maintenance', 'fg_dim')], cols)
    svg.add_table_row([('Culture', 'fg'), ('Stability', 'blue'), ('Stability', 'blue'), ('Stability', 'blue'), ('Builder', 'green')], cols)
    svg.add_table_row([('Phase', 'fg'), ('Declining', 'red'), ('Declining', 'red'), ('Declining', 'red'), ('Mature', 'green')], cols)
    svg.add_table_row([('Risk', 'fg'), ('Quality Drift', 'orange'), ('Quality Drift', 'orange'), ('Quality Drift', 'orange'), ('Design Vacuum', 'red')], cols)

    svg.add_blank()
    svg.add_text("Transitions:", color='aqua', bold=True)
    svg.add_colored_spans([("  [2025-H1] Character: ", 'fg'), ("Guardian", 'blue'), (" → ", 'fg_dim'), ("Factory", 'yellow')])
    svg.add_colored_spans([("  [2025-H1] Structure: ", 'fg'), ("Maintenance", 'fg_dim'), (" → ", 'fg_dim'), ("Delivery", 'yellow')])
    svg.add_colored_spans([("  [2025-H2] Character: ", 'fg'), ("Factory", 'yellow'), (" → ", 'fg_dim'), ("Guardian", 'blue')])
    svg.add_colored_spans([("  [2025-H2] Structure: ", 'fg'), ("Delivery", 'yellow'), (" → ", 'fg_dim'), ("Maintenance", 'fg_dim')])
    svg.save(os.path.join(IMG_DIR, 'ch6-frontend-team-timeline.svg'))


def ch6_infra_firmware():
    svg = TerminalSVG("Terminal — Infra & Firmware Classification", width=600)
    svg.add_text("═══ Infra (2026-H1) ═══", color='red', bold=True)
    svg.add_text("  Character:  Explorer", color='aqua')
    svg.add_text("  Structure:  Balanced", color='green')
    svg.add_text("  Culture:    Exploration", color='aqua')
    svg.add_text("  Phase:      Emerging", color='blue')
    svg.add_text("  Risk:       Design Vacuum", color='red')
    svg.add_blank()
    svg.add_text("═══ Firmware (2026-H1) ═══", color='red', bold=True)
    svg.add_text("  Character:  Firefighting", color='orange')
    svg.add_text("  Structure:  Maintenance Team", color='fg_dim')
    svg.add_text("  Culture:    Firefighting", color='orange')
    svg.add_text("  Phase:      Declining", color='red')
    svg.add_text("  Risk:       Design Vacuum", color='red')
    svg.save(os.path.join(IMG_DIR, 'ch6-infra-firmware.svg'))


def ch6_machuz_timeline():
    svg = TerminalSVG("machuz Backend Timeline", width=700)
    svg.add_text("--- machuz (Backend) ---", color='yellow', bold=True)
    rows = [
        ('2024-H1', '27.6', 'Anchor', '—', 'Growing'),
        ('2024-H2', '76.4', 'Anchor', 'Builder', ''),
        ('2025-H1', '58.4', 'Producer', 'Balanced', ''),
        ('2025-H2', '92.5', 'Architect', 'Builder', ''),
        ('2026-H1', '92.4', 'Architect', 'Builder', 'Active'),
    ]
    cols = [120, 60, 120, 120, 120]
    for r in rows:
        period, total, role, style, state = r
        cells = [
            (period, 'fg_dim'),
            (total, total_color(total), True),
            (role, role_color(role)),
            (style, 'blue' if style and style != '—' else 'fg_dim'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-machuz-timeline.svg'))


def ch6_be_architects():
    svg = TerminalSVG("Backend Architect Concentration", width=900)
    svg.add_text("Backend — Architect Seats Over Time", color='aqua', bold=True)
    svg.add_blank()
    cols = [100, 60, 170, 30, 60, 170]
    rows = [
        ('2024-H1', '93.5', 'Engineer F  Architect Builder', '', '27.6', 'machuz  Anchor'),
        ('2024-H2', '84.1', 'Engineer F  Architect Builder', '', '76.4', 'machuz  Anchor Builder'),
        ('2025-H1', '72.7', 'Engineer F  Anchor Balanced', '', '58.4', 'machuz  Producer'),
        ('2025-H2', '37.5', 'Engineer F  Anchor', '', '92.5', 'machuz  Architect Builder'),
    ]
    for r in rows:
        period, f_score, f_info, _, m_score, m_info = r
        f_color = 'purple' if 'Architect' in f_info else 'blue' if 'Anchor' in f_info else 'fg'
        m_color = 'purple' if 'Architect' in m_info else 'blue' if 'Anchor' in m_info else 'yellow'
        cells = [
            (period, 'fg_dim'),
            (f_score, total_color(f_score), True),
            (f_info, f_color),
            ('', 'fg'),
            (m_score, total_color(m_score), True),
            (m_info, m_color),
        ]
        svg.add_table_row(cells, cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-be-architects.svg'))


def ch6_fe_architects():
    svg = TerminalSVG("Frontend Architect Flow", width=900)
    svg.add_text("Frontend — Architect Seats Over Time", color='aqua', bold=True)
    svg.add_blank()
    cols = [100, 60, 170, 30, 60, 170]
    rows = [
        ('2024-H2', '72.7', 'Engineer I  Anchor', '', '74.9', 'Engineer J  Architect Builder'),
        ('2025-H1', '83.8', 'Engineer I  Architect', '', '54.3', 'Engineer J  Anchor'),
        ('2025-H2', '85.1', 'Engineer I  Architect', '', '38.6', 'Engineer J  Anchor'),
    ]
    for r in rows:
        period, i_score, i_info, _, j_score, j_info = r
        i_color = 'purple' if 'Architect' in i_info else 'blue'
        j_color = 'purple' if 'Architect' in j_info else 'blue'
        cells = [
            (period, 'fg_dim'),
            (i_score, total_color(i_score), True),
            (i_info, i_color),
            ('', 'fg'),
            (j_score, total_color(j_score), True),
            (j_info, j_color),
        ]
        svg.add_table_row(cells, cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-fe-architects.svg'))


def ch6_engineer_k():
    svg = TerminalSVG("Engineer K — Frontend Lifecycle", width=600)
    svg.add_text("--- Engineer K (Frontend) ---", color='yellow', bold=True)
    rows = [
        ('2024-H1', '87.8', 'Architect', 'Builder', ''),
        ('2024-H2', '14.6', '—', '—', ''),
        ('2025-H1', '7.1', '—', '—', 'Silent'),
        ('2025-H2', '3.2', '—', '—', ''),
        ('2026-H1', '3.2', '—', '—', ''),
    ]
    cols = [120, 60, 120, 120, 120]
    for r in rows:
        period, total, role, style, state = r
        cells = [
            (period, 'fg_dim'),
            (total, total_color(total), True),
            (role, role_color(role)),
            (style, 'blue' if style and style != '—' else 'fg_dim'),
            (state, state_color(state)),
        ]
        svg.add_table_row(cells, cols)
    svg.save(os.path.join(IMG_DIR, 'ch6-engineer-k.svg'))


def ch6_gravity_transfer():
    svg = TerminalSVG("Gravity Transfer — Frontend", width=700)
    svg.add_text("Score Transfer:", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("Engineer K:  ", 'yellow'), ("87.8", 'purple', True), (" → ", 'fg_dim'), ("14.6", 'fg'), (" → ", 'fg_dim'), ("7.1", 'fg_dim'), (" → ", 'fg_dim'), ("3.2", 'fg_dim'), (" → ", 'fg_dim'), ("3.2", 'fg_dim')])
    svg.add_colored_spans([("Engineer I:  ", 'yellow'), ("  — ", 'fg_dim'), (" → ", 'fg_dim'), ("72.7", 'green'), (" → ", 'fg_dim'), ("83.8", 'purple', True), (" → ", 'fg_dim'), ("85.1", 'purple', True), (" → ", 'fg_dim'), ("78.1", 'green')])
    svg.add_colored_spans([("Engineer J:  ", 'yellow'), ("25.9", 'fg'), (" → ", 'fg_dim'), ("74.9", 'green'), (" → ", 'fg_dim'), ("54.3", 'green'), (" → ", 'fg_dim'), ("38.6", 'yellow'), (" → ", 'fg_dim'), ("54.2", 'green')])
    svg.save(os.path.join(IMG_DIR, 'ch6-gravity-transfer.svg'))


def ch6_evolution_paths():
    svg = TerminalSVG("Evolution Paths", width=800)
    svg.add_text("Evolution Paths:", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("machuz:     ", 'yellow'), ("Anchor", 'blue'), (" → ", 'fg_dim'), ("Anchor Builder", 'blue'), (" → ", 'fg_dim'), ("Producer Balanced", 'yellow'), (" → ", 'fg_dim'), ("Architect Builder", 'purple', True)])
    svg.add_colored_spans([("Engineer I: ", 'yellow'), ("Anchor Balanced", 'blue'), (" → ", 'fg_dim'), ("Architect Balanced", 'purple'), (" → ", 'fg_dim'), ("Architect Builder", 'purple', True)])
    svg.add_colored_spans([("Engineer J: ", 'yellow'), ("Anchor Growing", 'blue'), (" → ", 'fg_dim'), ("Architect Balanced", 'purple'), (" → ", 'fg_dim'), ("Architect Builder", 'purple', True)])
    svg.add_colored_spans([("Engineer F: ", 'yellow'), ("(first appearance) ", 'fg_dim'), ("Architect Builder", 'purple', True)])
    svg.save(os.path.join(IMG_DIR, 'ch6-evolution-paths.svg'))


def ch6_evolution_model():
    svg = TerminalSVG("Evolution Model Overview", width=750)
    lines = [
        ("┌──────────────────────────────────────────────────────────┐", 'fg_dim'),
        ("│              Evolution Model Overview                    │", 'aqua'),
        ("├──────────────────────────────────────────────────────────┤", 'fg_dim'),
        ("│                                                          │", 'fg_dim'),
    ]
    for text, color in lines:
        svg.add_text(text, color=color)

    svg.add_colored_spans([("│  ", 'fg_dim'), ("[Growing]", 'blue'), (" → ", 'fg_dim'), ("[Anchor]", 'blue'), (" → ", 'fg_dim'), ("[Producer]", 'yellow'), (" → ", 'fg_dim'), ("[Architect]", 'purple'), ("        │", 'fg_dim')])
    svg.add_text("│                  ↑            │            │             │", color='fg_dim')
    svg.add_text("│                  │            │   structure │             │", color='fg_dim')
    svg.add_text("│                  │            ←─────────────┘             │", color='fg_dim')
    svg.add_text("│                  │       (metabolism: back to Producer)   │", color='fg_dim')
    svg.add_text("│                                                          │", color='fg_dim')

    svg.add_colored_spans([("│  * Permeation: ", 'fg_dim'), ("[Anchor]", 'blue'), (" → ", 'fg_dim'), ("[Producer]", 'yellow'), (" → ", 'fg_dim'), ("[Architect]", 'purple'), ("        │", 'fg_dim')])
    svg.add_colored_spans([("│  * Immediate:  ", 'fg_dim'), ("[Anchor]", 'blue'), (" → ", 'fg_dim'), ("[Architect]", 'purple'), (" direct               │", 'fg_dim')])
    svg.add_colored_spans([("│  * Founding:   ", 'fg_dim'), ("[Architect]", 'purple'), (" → score decline (= success)   │", 'fg_dim')])
    svg.add_text("│                                                          │", color='fg_dim')
    svg.add_text("├──────────────────────────────────────────────────────────┤", color='fg_dim')
    svg.add_colored_spans([("│  BE: Architect seats tend to ", 'fg'), ("concentrate", 'red'), (" (observed: 1)    │", 'fg')])
    svg.add_colored_spans([("│  FE: Architect seats are ", 'fg'), ("fluid", 'green'), (" (observed: 1–2)           │", 'fg')])
    svg.add_text("├──────────────────────────────────────────────────────────┤", color='fg_dim')
    svg.add_text("│  Builder prerequisite: Builder experience → Architect    │", color='fg')
    svg.add_text("│  Producer fuel: using structure deeply powers design     │", color='fg')
    svg.add_colored_spans([("│  Producer Vacuum: no producers = ", 'fg'), ("structure sits idle", 'red'), ("      │", 'fg')])
    svg.add_text("└──────────────────────────────────────────────────────────┘", color='fg_dim')
    svg.save(os.path.join(IMG_DIR, 'ch6-evolution-model.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 7 — Universe of Code
# ════════════════════════════════════════════════════════════

def ch7_team_classification():
    svg = TerminalSVG("Terminal — Team Timeline Classification", width=800)
    svg.add_text("Classification:", color='aqua', bold=True)
    cols = [120, 180, 180, 190]
    svg.add_table_row([('Period', 'fg_dim'), ('2024-H1', 'fg_dim'), ('2024-H2', 'fg_dim'), ('2025-H1', 'fg_dim')], cols)
    svg.add_table_row([('Character', 'fg'), ('Elite', 'yellow', True), ('Guardian', 'blue'), ('Elite', 'yellow', True)], cols)
    svg.add_table_row([('Structure', 'fg'), ('Architectural Team', 'purple'), ('Maintenance Team', 'fg_dim'), ('Architectural Engine', 'purple', True)], cols)
    svg.add_table_row([('Risk', 'fg'), ('Bus Factor', 'orange'), ('Design Vacuum', 'red'), ('Healthy', 'green')], cols)
    svg.save(os.path.join(IMG_DIR, 'ch7-team-classification.svg'))


# ════════════════════════════════════════════════════════════
# CHAPTER 8 — Engineering Relativity
# ════════════════════════════════════════════════════════════

def ch8_repo_scores():
    svg = TerminalSVG("Same Engineer, Different Universes", width=600)
    svg.add_colored_spans([("Repo A (Backend API)           Total: ", 'fg'), ("35", 'yellow', True)])
    svg.add_colored_spans([("Repo B (New microservice)      Total: ", 'fg'), ("60", 'green', True)])
    svg.save(os.path.join(IMG_DIR, 'ch8-repo-scores.svg'))


def ch8_structure_comparison():
    svg = TerminalSVG("Gravitational Field Strength", width=800)
    svg.add_colored_spans([("Structure: ", 'fg'), ("Architectural Engine", 'purple', True), ("  →  Strong gravitational field", 'fg_dim')])
    svg.add_text("                                  (scores are hard-earned)", color='fg_dim')
    svg.add_blank()
    svg.add_colored_spans([("Structure: ", 'fg'), ("Unstructured", 'red', True), ("          →  Weak gravitational field", 'fg_dim')])
    svg.add_text("                                  (scores come easily)", color='fg_dim')
    svg.save(os.path.join(IMG_DIR, 'ch8-structure-comparison.svg'))


def ch8_per_repo_breakdown():
    svg = TerminalSVG("Terminal — eis analyze --recursive --per-repo", width=800)
    svg.add_command("eis analyze --recursive --per-repo ~/workspace")
    svg.add_blank()
    svg.add_text("─── Backend Per-Repository Breakdown ───", color='red', bold=True)
    svg.add_blank()

    cols = [100, 160, 150, 150, 160]
    svg.add_table_row([('Author', 'aqua', True), ('api-manage', 'aqua', True), ('api', 'aqua', True), ('worker', 'aqua', True), ('Pattern', 'aqua', True)], cols)
    svg.add_separator()
    svg.add_table_row([('machuz', 'yellow'), ('Architect 94', 'purple', True), ('Architect 73', 'purple'), ('Architect 76', 'purple'), ('Reproducible', 'green', True)], cols)
    svg.add_table_row([('alice', 'yellow'), ('Producer 34', 'yellow'), ('Architect 71', 'purple'), ('30', 'fg'), ('Context-dependent', 'blue')], cols)
    svg.add_table_row([('bob', 'yellow'), ('Anchor 41', 'blue'), ('30', 'fg'), ('Cleaner 34', 'aqua'), ('Variable', 'fg_dim')], cols)
    svg.save(os.path.join(IMG_DIR, 'ch8-per-repo-breakdown.svg'))


# ════════════════════════════════════════════════════════════
# COVER IMAGES
# ════════════════════════════════════════════════════════════

def cover_image(chapter, title, subtitle, visual_fn):
    """Create a chapter cover image."""
    svg = TerminalSVG(f"Engineering Impact Score — Chapter {chapter}", width=1200)
    svg.y = 70
    svg.add_text(f"Chapter {chapter}", color='fg_dim')
    svg.add_blank()
    svg.add_text(title, color='yellow', bold=True)
    # override font size for title
    svg.lines[-1] = svg.lines[-1].replace(f'font-size="{FONT_SIZE}"', 'font-size="24"')
    svg.add_blank()
    svg.add_text(subtitle, color='fg_dim')
    svg.lines[-1] = svg.lines[-1].replace(f'font-size="{FONT_SIZE}"', 'font-size="14"')
    svg.add_blank(2)

    visual_fn(svg)

    svg.save(os.path.join(IMG_DIR, f'cover-ch{chapter}.svg'))


def cover_ch1_visual(svg):
    svg.add_text("  7-Axis Scoring Model", color='aqua', bold=True)
    svg.add_blank()
    bars = [
        ('Production', 75, 'green'),
        ('Quality', 64, 'green'),
        ('Survival', 100, 'purple'),
        ('Design', 85, 'purple'),
        ('Breadth', 60, 'green'),
        ('Debt', 78, 'green'),
        ('Indispensability', 43, 'yellow'),
    ]
    for name, val, color in bars:
        bar = '█' * (val // 5) + '░' * (20 - val // 5)
        svg.add_colored_spans([
            (f"  {name:<20}", 'fg'),
            (bar, color),
            (f"  {val}", color, True),
        ])


def cover_ch2_visual(svg):
    svg.add_text("  Team Health Radar", color='aqua', bold=True)
    svg.add_blank()
    axes = [
        ('Complementarity', 72, 'green'),
        ('Growth Potential', 58, 'green'),
        ('Sustainability', 45, 'yellow'),
        ('Productivity', 67, 'green'),
        ('Quality', 81, 'purple'),
        ('Bus Factor', 35, 'red'),
        ('Gravity Health', 62, 'green'),
    ]
    for name, val, color in axes:
        bar = '█' * (val // 5) + '░' * (20 - val // 5)
        svg.add_colored_spans([
            (f"  {name:<20}", 'fg'),
            (bar, color),
            (f"  {val}", color, True),
        ])


def cover_ch3_visual(svg):
    svg.add_text("  Archetypes", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  ◆ ", 'purple'), ("Architect", 'purple', True), ("  — Creates gravity, shapes codebase structure", 'fg_dim')])
    svg.add_colored_spans([("  ◆ ", 'blue'), ("Anchor", 'blue', True), ("     — Maintains orbit, stabilizes code", 'fg_dim')])
    svg.add_colored_spans([("  ◆ ", 'yellow'), ("Producer", 'yellow', True), ("   — Generates output, uses structure", 'fg_dim')])
    svg.add_colored_spans([("  ◆ ", 'aqua'), ("Cleaner", 'aqua', True), ("    — Reduces entropy, improves quality", 'fg_dim')])
    svg.add_blank()
    svg.add_colored_spans([("  Builder → Mass → Balanced → Spread → Churn → Rescue", 'fg_dim')])


def cover_ch4_visual(svg):
    svg.add_text("  Backend Architect Concentration", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  2024-H1  ", 'fg_dim'), ("★", 'purple'), (" Engineer F  ●", 'blue'), (" machuz", 'fg_dim')])
    svg.add_colored_spans([("  2024-H2  ", 'fg_dim'), ("★", 'purple'), (" Engineer F  ●", 'blue'), (" machuz (Builder)", 'blue')])
    svg.add_colored_spans([("  2025-H1  ", 'fg_dim'), ("●", 'blue'), (" Engineer F  ●", 'yellow'), (" machuz", 'fg_dim')])
    svg.add_colored_spans([("  2025-H2  ", 'fg_dim'), ("●", 'fg_dim'), (" Engineer F  ", 'fg_dim'), ("★", 'purple'), (" machuz (Architect)", 'purple', True)])
    svg.add_blank()
    svg.add_text("  The seat converges to one. Always.", color='fg_dim')


def cover_ch5_visual(svg):
    svg.add_text("  Timeline — Scores Don't Lie", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  Q1  ", 'fg_dim'), ("████████████████████", 'purple'), ("  90.0  Architect", 'purple')])
    svg.add_colored_spans([("  Q2  ", 'fg_dim'), ("██████████████████", 'green'), ("    72.5  Producer", 'yellow')])
    svg.add_colored_spans([("  Q3  ", 'fg_dim'), ("█████████████", 'yellow'), ("         49.1  Anchor", 'blue')])
    svg.add_colored_spans([("  Q4  ", 'fg_dim'), ("███████", 'red'), ("               31.2  — Fragile", 'red')])
    svg.add_colored_spans([("  Q1  ", 'fg_dim'), ("███", 'fg_dim'), ("                   11.3  — Former", 'fg_dim')])
    svg.add_blank()
    svg.add_text("  Hesitation leaves traces in the data.", color='fg_dim')


def cover_ch6_visual(svg):
    svg.add_text("  Team Evolution Models", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  Growing", 'blue'), (" → ", 'fg_dim'), ("Anchor", 'blue'), (" → ", 'fg_dim'), ("Producer", 'yellow'), (" → ", 'fg_dim'), ("Architect", 'purple', True)])
    svg.add_blank()
    svg.add_colored_spans([("  Permeation:  ", 'fg'), ("respect → produce → design", 'aqua')])
    svg.add_colored_spans([("  Immediate:   ", 'fg'), ("Anchor → Architect (rare)", 'purple')])
    svg.add_colored_spans([("  Founding:    ", 'fg'), ("Architect → decline = success", 'green')])
    svg.add_blank()
    svg.add_text("  Organizations have laws. Timelines reveal them.", color='fg_dim')


def cover_ch7_visual(svg):
    svg.add_text("  The Universe of Code", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  ◉ ", 'purple'), ("Gravity     ", 'fg'), ("— Architects create gravitational centers", 'fg_dim')])
    svg.add_colored_spans([("  ◉ ", 'green'), ("Strong Force", 'fg'), (" — Domain coupling holds modules together", 'fg_dim')])
    svg.add_colored_spans([("  ◉ ", 'blue'), ("Weak Force  ", 'fg'), (" — Cross-domain interactions and decay", 'fg_dim')])
    svg.add_colored_spans([("  ◉ ", 'yellow'), ("EM Force    ", 'fg'), (" — Communication patterns between members", 'fg_dim')])
    svg.add_blank()
    svg.add_text("  Codebases are universes. Engineers are celestial bodies.", color='fg_dim')


def cover_ch8_visual(svg):
    svg.add_text("  Engineering Relativity", color='aqua', bold=True)
    svg.add_blank()
    svg.add_colored_spans([("  Same engineer, different universes:", 'fg')])
    svg.add_blank()
    svg.add_colored_spans([("    Repo A  ", 'fg_dim'), ("Architectural Engine", 'purple'), ("  →  Total: ", 'fg'), ("35", 'yellow', True), ("  (hard-earned)", 'fg_dim')])
    svg.add_colored_spans([("    Repo B  ", 'fg_dim'), ("Unstructured", 'red'), ("          →  Total: ", 'fg'), ("60", 'green', True), ("  (easy)", 'fg_dim')])
    svg.add_blank()
    svg.add_text("  The gravity depends on the space it exists in.", color='fg_dim')


# ════════════════════════════════════════════════════════════
# CODE CARD GENERATORS
# ════════════════════════════════════════════════════════════


# ── Chapter 1 Code Cards ──

def ch1_formula_production():
    c = CodeCardSVG('formula', width=720)
    c.add_spans([
        ('production_score', 'blue'), (' = ', 'fg_dim'), ('min', 'yellow'), ('(', 'fg_dim'),
        ('changes_per_day', 'fg'), (' / ', 'fg_dim'), ('production_daily_ref', 'fg'),
        (' × ', 'fg_dim'), ('100', 'purple'), (', ', 'fg_dim'), ('100', 'purple'), (')', 'fg_dim'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch1-formula-production.svg'))


def ch1_formula_quality():
    c = CodeCardSVG('formula', width=560)
    c.add_spans([
        ('quality', 'blue'), (' = ', 'fg_dim'), ('100', 'purple'), (' - ', 'fg_dim'), ('fix_ratio', 'fg'),
    ])
    c.add_spans([
        ('fix_ratio', 'blue'), (' = ', 'fg_dim'), ('fix_commits', 'fg'), (' / ', 'fg_dim'),
        ('total_commits', 'fg'), (' × ', 'fg_dim'), ('100', 'purple'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch1-formula-quality.svg'))


def ch1_code_survival():
    c = CodeCardSVG('python', width=620)
    c.add_spans([('import', 'red'), (' math', 'fg')])
    c.add_spans([('from', 'red'), (' collections ', 'fg'), ('import', 'red'), (' defaultdict', 'fg')])
    c.add_blank()
    c.add_spans([('tau', 'blue'), (' = ', 'fg_dim'), ('180', 'purple'), ('  ', 'fg'), ('# days', 'fg_dim')])
    c.add_blank()
    c.add_spans([('weighted_survival', 'blue'), (' = ', 'fg_dim'), ('defaultdict', 'yellow'), ('(', 'fg_dim'), ('float', 'aqua'), (')', 'fg_dim')])
    c.add_spans([('for', 'red'), (' line ', 'fg'), ('in', 'red'), (' blame_lines:', 'fg')])
    c.add_spans([('    days_alive', 'fg'), (' = ', 'fg_dim'), ('(now - line.committer_time).days', 'fg')])
    c.add_spans([('    weight', 'blue'), (' = ', 'fg_dim'), ('math.exp', 'yellow'), ('(', 'fg_dim'), ('-days_alive / tau', 'fg'), (')', 'fg_dim')])
    c.add_spans([('    weighted_survival', 'fg'), ('[line.author]', 'fg'), (' += ', 'fg_dim'), ('weight', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch1-code-survival.svg'))


def ch1_code_debt():
    c = CodeCardSVG('python', width=620)
    c.add_spans([('for', 'red'), (' fix_commit ', 'fg'), ('in', 'red'), (' fix_commits:', 'fg')])
    c.add_spans([('    fixer', 'blue'), (' = ', 'fg_dim'), ('fix_commit.author', 'fg')])
    c.add_spans([('    ', 'fg'), ('for', 'red'), (' changed_line ', 'fg'), ('in', 'red'), (' fix_commit.changed_lines:', 'fg')])
    c.add_spans([('        original_author', 'blue'), (' = ', 'fg_dim'), ('git_blame', 'yellow'), ('(file, at=parent_commit)', 'fg')])
    c.add_spans([('        ', 'fg'), ('if', 'red'), (' original_author != fixer:', 'fg')])
    c.add_spans([('            debt_generated', 'fg'), ('[original_author]', 'fg'), (' += ', 'fg_dim'), ('1', 'purple')])
    c.add_spans([('            debt_cleaned', 'fg'), ('[fixer]', 'fg'), (' += ', 'fg_dim'), ('1', 'purple')])
    c.add_blank()
    c.add_spans([('debt_ratio', 'blue'), (' = ', 'fg_dim'), ('debt_cleaned', 'fg'), (' / ', 'fg_dim'), ('max', 'yellow'), ('(debt_generated, ', 'fg'), ('1', 'purple'), (')', 'fg_dim')])
    c.add_line('# > 1 = Cleaner  |  < 1 = Debt creator', color='fg_dim')
    c.save(os.path.join(IMG_DIR, 'ch1-code-debt.svg'))


def ch1_code_indispensability():
    c = CodeCardSVG('python', width=640)
    c.add_spans([('for', 'red'), (' module ', 'fg'), ('in', 'red'), (' all_modules:', 'fg')])
    c.add_spans([('    top_share', 'blue'), (' = ', 'fg_dim'), ('max', 'yellow'), ('(blame_distribution[module].values())', 'fg'), (' / ', 'fg_dim'), ('total', 'fg')])
    c.add_spans([('    ', 'fg'), ('if', 'red'), (' top_share >= ', 'fg'), ('0.8', 'purple'), (':', 'fg')])
    c.add_spans([('        critical_modules', 'fg'), ('[top_author].append(module)', 'fg')])
    c.add_spans([('    ', 'fg'), ('elif', 'red'), (' top_share >= ', 'fg'), ('0.6', 'purple'), (':', 'fg')])
    c.add_spans([('        high_risk_modules', 'fg'), ('[top_author].append(module)', 'fg')])
    c.add_blank()
    c.add_spans([
        ('indispensability', 'blue'), (' = ', 'fg_dim'),
        ('critical_count', 'fg'), (' × ', 'fg_dim'), ('1.0', 'purple'),
        (' + ', 'fg_dim'), ('high_count', 'fg'), (' × ', 'fg_dim'), ('0.5', 'purple'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch1-code-indispensability.svg'))


def ch1_formula_total():
    c = CodeCardSVG('formula', width=480)
    c.add_spans([('score', 'blue'), (' =', 'fg_dim')])
    for name, weight in [('production', '0.15'), ('quality', '0.10'), ('survival', '0.25'),
                          ('design', '0.20'), ('breadth', '0.10'), ('debt_cleanup', '0.15'),
                          ('indispensability', '0.05')]:
        prefix = '  ' if name == 'production' else '  + '
        c.add_spans([(prefix, 'fg_dim'), (name, 'fg'), (' × ', 'fg_dim'), (weight, 'purple')])
    c.save(os.path.join(IMG_DIR, 'ch1-formula-total.svg'))


def ch1_formula_gravity():
    c = CodeCardSVG('formula', width=720)
    c.add_spans([
        ('Gravity', 'blue'), (' = ', 'fg_dim'),
        ('Indispensability', 'fg'), (' × ', 'fg_dim'), ('0.40', 'purple'),
        (' + ', 'fg_dim'), ('Breadth', 'fg'), (' × ', 'fg_dim'), ('0.30', 'purple'),
        (' + ', 'fg_dim'), ('Design', 'fg'), (' × ', 'fg_dim'), ('0.30', 'purple'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch1-formula-gravity.svg'))


def ch1_formula_gravity_health():
    c = CodeCardSVG('formula', width=660, label='Formula')
    c.add_spans([
        ('health', 'blue'), (' = ', 'fg_dim'),
        ('Quality', 'fg'), (' × ', 'fg_dim'), ('0.6', 'purple'),
        (' + ', 'fg_dim'), ('RobustSurvival', 'fg'), (' × ', 'fg_dim'), ('0.4', 'purple'),
    ])
    c.add_blank()
    c.add_spans([('Gravity < 20', 'fg'), ('  → ', 'fg_dim'), ('dim gray', 'fg_dim'), (' (low influence)', 'fg_dim')])
    c.add_spans([('health ≥ 60', 'fg'), ('  → ', 'fg_dim'), ('green', 'green'), (' (healthy gravity)', 'fg_dim')])
    c.add_spans([('health ≥ 40', 'fg'), ('  → ', 'fg_dim'), ('yellow', 'yellow'), (' (moderate)', 'fg_dim')])
    c.add_spans([('health < 40', 'fg'), ('  → ', 'fg_dim'), ('red', 'red'), (' (fragile gravity)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch1-formula-gravity-health.svg'))


def ch1_bash_install():
    c = CodeCardSVG('bash', width=420)
    c.add_spans([('brew', 'green'), (' tap machuz/tap', 'fg')])
    c.add_spans([('brew', 'green'), (' install eis', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch1-bash-install.svg'))


def ch1_bash_usage():
    c = CodeCardSVG('bash', width=580)
    c.add_line('# Analyze current repo', color='fg_dim')
    c.add_spans([('eis', 'green'), (' analyze .', 'fg')])
    c.add_blank()
    c.add_line('# Auto-discover repos under a directory', color='fg_dim')
    c.add_spans([('eis', 'green'), (' analyze --recursive ~/projects', 'fg')])
    c.add_blank()
    c.add_line('# With config', color='fg_dim')
    c.add_spans([('eis', 'green'), (' analyze --config eis.yaml --recursive ~/projects', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch1-bash-usage.svg'))


def ch1_bash_gitlog():
    """JA-only: git log command."""
    c = CodeCardSVG('bash', width=620)
    c.add_spans([('git', 'green'), (' log --all --no-merges --format=', 'fg'), ('"COMMIT:%an||%s"', 'yellow'), (' --numstat', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch1-bash-gitlog.svg'))


def ch1_code_fixdetect():
    """JA-only: fix detection regex."""
    c = CodeCardSVG('python', width=720)
    c.add_spans([('is_fix', 'blue'), (' = ', 'fg_dim'), ('re.match', 'yellow'), ('(', 'fg_dim'),
                 ('r"^(fix|revert|hotfix)"', 'green'), (', subject.lower())', 'fg')])
    c.add_spans([('        ', 'fg'), ('or', 'red'), (' ', 'fg'), ('"修正"', 'green'), (' ', 'fg'), ('in', 'red'), (' subject', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch1-code-fixdetect.svg'))


def ch1_yaml_config():
    """JA-only: eis.yaml example."""
    c = CodeCardSVG('yaml', width=500)
    c.add_spans([('aliases', 'blue'), (':', 'fg_dim')])
    c.add_spans([('  ', 'fg'), ('"John Smith"', 'green'), (': ', 'fg_dim'), ('"john"', 'green')])
    c.add_spans([('  ', 'fg'), ('"J. Smith"', 'green'), (': ', 'fg_dim'), ('"john"', 'green')])
    c.add_spans([('exclude_authors', 'blue'), (':', 'fg_dim')])
    c.add_spans([('  - ', 'fg_dim'), ('"dependabot[bot]"', 'green')])
    c.add_spans([('domains', 'blue'), (':', 'fg_dim')])
    c.add_spans([('  ', 'fg'), ('backend', 'aqua'), (': ', 'fg_dim'), ('[', 'fg_dim'), ('"api-*"', 'green'), (', ', 'fg_dim'), ('"worker"', 'green'), (']', 'fg_dim')])
    c.add_spans([('  ', 'fg'), ('frontend', 'aqua'), (': ', 'fg_dim'), ('[', 'fg_dim'), ('"web-*"', 'green'), (', ', 'fg_dim'), ('"app"', 'green'), (']', 'fg_dim')])
    c.add_spans([('  ', 'fg'), ('firmware', 'aqua'), (': ', 'fg_dim'), ('[', 'fg_dim'), ('"raden"', 'green'), (']', 'fg_dim')])
    c.add_spans([('exclude_repos', 'blue'), (': ', 'fg_dim'), ('[', 'fg_dim'), ('"deprecated-service"', 'green'), (']', 'fg_dim')])
    c.add_spans([('production_daily_ref', 'blue'), (': ', 'fg_dim'), ('1000', 'purple')])
    c.add_spans([('tau', 'blue'), (': ', 'fg_dim'), ('180', 'purple')])
    c.save(os.path.join(IMG_DIR, 'ch1-yaml-config.svg'))


# ── Chapter 2 Code Cards ──

def ch2_bash_team():
    c = CodeCardSVG('bash', width=580)
    c.add_line('# Simplest: domain = team', color='fg_dim')
    c.add_spans([('eis', 'green'), (' team --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# With explicit team definitions', color='fg_dim')
    c.add_spans([('eis', 'green'), (' team --config eis.yaml --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# JSON output', color='fg_dim')
    c.add_spans([('eis', 'green'), (' team --format json --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch2-bash-team.svg'))


def ch2_yaml_teams():
    c = CodeCardSVG('yaml', width=440)
    c.add_line('# eis.yaml (optional)', color='fg_dim')
    c.add_spans([('teams', 'blue'), (':', 'fg_dim')])
    c.add_spans([('  ', 'fg'), ('backend-core', 'aqua'), (':', 'fg_dim')])
    c.add_spans([('    ', 'fg'), ('domain', 'blue'), (': ', 'fg_dim'), ('Backend', 'green')])
    c.add_spans([('    ', 'fg'), ('members', 'blue'), (': ', 'fg_dim'), ('[alice, bob, charlie]', 'fg')])
    c.add_spans([('  ', 'fg'), ('frontend-app', 'aqua'), (':', 'fg_dim')])
    c.add_spans([('    ', 'fg'), ('domain', 'blue'), (': ', 'fg_dim'), ('Frontend', 'green')])
    c.add_spans([('    ', 'fg'), ('members', 'blue'), (': ', 'fg_dim'), ('[dave, eve]', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch2-yaml-teams.svg'))


def ch2_formula_complementarity():
    c = CodeCardSVG('formula', width=580)
    c.add_spans([('coverage', 'blue'), (' = ', 'fg_dim'), ('uniqueRoles', 'fg'), (' / ', 'fg_dim'), ('5', 'purple')])
    c.add_spans([('bonus', 'blue'), (' = ', 'fg_dim'), ('Architect', 'purple'), ('(+10)', 'fg_dim'),
                 (' + ', 'fg_dim'), ('Anchor', 'blue'), ('(+5)', 'fg_dim'),
                 (' + ', 'fg_dim'), ('Cleaner', 'aqua'), ('(+5)', 'fg_dim')])
    c.add_spans([('score', 'blue'), (' = ', 'fg_dim'), ('coverage', 'fg'), (' × ', 'fg_dim'), ('80', 'purple'),
                 (' + ', 'fg_dim'), ('bonus', 'fg'), ('  ', 'fg'), ('(clamped 0-100)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-complementarity.svg'))


def ch2_formula_growth():
    c = CodeCardSVG('formula', width=580)
    c.add_spans([('score', 'blue'), (' = ', 'fg_dim'), ('growingRatio', 'fg'), (' × ', 'fg_dim'), ('60', 'purple'),
                 (' + ', 'fg_dim'), ('Builder', 'green'), ('(+20)', 'fg_dim'),
                 (' + ', 'fg_dim'), ('Cleaner', 'aqua'), ('(+20)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-growth.svg'))


def ch2_formula_sustainability():
    c = CodeCardSVG('formula', width=620)
    c.add_spans([('riskRatio', 'blue'), (' = ', 'fg_dim'), ('(Former + Silent + Fragile)', 'fg'), (' / ', 'fg_dim'), ('memberCount', 'fg')])
    c.add_spans([('score', 'blue'), (' = ', 'fg_dim'), ('(1 - riskRatio)', 'fg'), (' × ', 'fg_dim'), ('80', 'purple'),
                 (' + ', 'fg_dim'), ('Architect', 'purple'), ('(+20)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-sustainability.svg'))


def ch2_formula_productivity():
    c = CodeCardSVG('formula', width=520)
    c.add_spans([('base', 'blue'), (' = ', 'fg_dim'), ('avg', 'yellow'), ('(members.Production)', 'fg')])
    c.add_spans([('bonus:', 'fg_dim')])
    c.add_spans([('  ≤3 members', 'fg'), (' && ', 'fg_dim'), ('base ≥ 50', 'fg'), (' → ', 'fg_dim'), ('×1.2', 'green')])
    c.add_spans([('  ≤5 members', 'fg'), (' && ', 'fg_dim'), ('base ≥ 50', 'fg'), (' → ', 'fg_dim'), ('×1.1', 'green')])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-productivity.svg'))


def ch2_formula_quality_consistency():
    c = CodeCardSVG('formula', width=620)
    c.add_spans([
        ('score', 'blue'), (' = ', 'fg_dim'),
        ('avgQuality', 'fg'), (' × ', 'fg_dim'), ('0.6', 'purple'),
        (' + ', 'fg_dim'), ('(100 - stdev × 2)', 'fg'), (' × ', 'fg_dim'), ('0.4', 'purple'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-quality-consistency.svg'))


def ch2_formula_weight():
    c = CodeCardSVG('formula', width=520)
    c.add_spans([
        ('weight', 'blue'), (' = ', 'fg_dim'),
        ('member.Total', 'fg'), (' / ', 'fg_dim'), ('100', 'purple'),
        ('  ', 'fg'), ('(minimum 0.1)', 'fg_dim'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-weight.svg'))


def ch2_diagram_growth_model():
    c = CodeCardSVG('diagram', width=620, label='Model')
    c.add_spans([('  Design Layer        ', 'fg'), ('Architect', 'purple', True)])
    c.add_spans([('                      ', 'fg'), ('↑ Design decisions embedded in code', 'fg_dim')])
    c.add_line('  ──────────────────────────────────', color='separator')
    c.add_spans([('  Stabilization Layer ', 'fg'), ('Anchor', 'blue', True), (' / ', 'fg_dim'), ('Cleaner', 'aqua', True)])
    c.add_spans([('                      ', 'fg'), ('↑ Quality rises, code survives', 'fg_dim')])
    c.add_line('  ──────────────────────────────────', color='separator')
    c.add_spans([('  Implementation Layer ', 'fg'), ('Producer', 'yellow', True), (' / ', 'fg_dim'), ('Growing', 'blue', True)])
    c.add_spans([('                       ', 'fg'), ('Write code. Ship it.', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch2-diagram-growth-model.svg'))


def ch2_diagram_decline():
    c = CodeCardSVG('diagram', width=680, label='Model')
    c.add_spans([('  Design Layer        ', 'fg'), ('→ ', 'fg_dim'), ('Former', 'fg_dim'), (' (design knowledge leaves)', 'fg_dim')])
    c.add_spans([('  Stabilization Layer ', 'fg'), ('→ ', 'fg_dim'), ('Silent', 'fg_dim'), (', ', 'fg_dim'), ('Fragile', 'red')])
    c.add_spans([('  Implementation Layer ', 'fg'), ('→ ', 'fg_dim'), ('Silent', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch2-diagram-decline.svg'))


def ch2_bash_install_team():
    c = CodeCardSVG('bash', width=620)
    c.add_line('# Install', color='fg_dim')
    c.add_spans([('brew', 'green'), (' tap machuz/tap && ', 'fg'), ('brew', 'green'), (' install eis', 'fg')])
    c.add_blank()
    c.add_line('# Team analysis', color='fg_dim')
    c.add_spans([('eis', 'green'), (' team --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# JSON → paste into AI', color='fg_dim')
    c.add_spans([('eis', 'green'), (' team --format json --recursive ~/workspace | pbcopy', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch2-bash-install-team.svg'))


def ch2_formula_debt_balance():
    """JA-only: Debt Balance formula."""
    c = CodeCardSVG('formula', width=520)
    c.add_spans([
        ('score', 'blue'), (' = ', 'fg_dim'), ('avg', 'yellow'), ('(members.DebtCleanup)', 'fg'),
        ('  ', 'fg'), ('// 0-100', 'fg_dim'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-debt-balance.svg'))


def ch2_formula_risk_ratio():
    """JA-only: Risk Ratio formula."""
    c = CodeCardSVG('formula', width=720)
    c.add_spans([
        ('riskRatio', 'blue'), (' = ', 'fg_dim'),
        ('(Former + Silent + Fragile)', 'fg'), (' / ', 'fg_dim'),
        ('memberCount', 'fg'), (' × ', 'fg_dim'), ('100', 'purple'),
        ('  ', 'fg'), ('(%)', 'fg_dim'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch2-formula-risk-ratio.svg'))


# ── Chapter 3 Code Cards ──

def ch3_gravity_calc_d():
    c = CodeCardSVG('formula', width=560)
    c.add_spans([('100', 'purple'), (' × ', 'fg_dim'), ('0.4', 'purple'), (' + ', 'fg_dim'),
                 ('88', 'purple'), (' × ', 'fg_dim'), ('0.3', 'purple'), (' + ', 'fg_dim'),
                 ('5', 'fg_dim'), (' × ', 'fg_dim'), ('0.3', 'purple'), (' = ', 'fg_dim'), ('68', 'yellow', True)])
    c.save(os.path.join(IMG_DIR, 'ch3-gravity-calc-d.svg'))


def ch3_gravity_calc_a():
    c = CodeCardSVG('formula', width=560)
    c.add_spans([('60', 'yellow'), (' × ', 'fg_dim'), ('0.4', 'purple'), (' + ', 'fg_dim'),
                 ('100', 'purple'), (' × ', 'fg_dim'), ('0.3', 'purple'), (' + ', 'fg_dim'),
                 ('100', 'purple'), (' × ', 'fg_dim'), ('0.3', 'purple'), (' = ', 'fg_dim'), ('84', 'purple', True)])
    c.save(os.path.join(IMG_DIR, 'ch3-gravity-calc-a.svg'))


def ch3_data_warning():
    c = CodeCardSVG('data', width=780, label='Warning')
    c.add_spans([('⚠ ', 'yellow'), ('Warnings:', 'yellow', True)])
    c.add_spans([('  Fragile gravity — ', 'fg'), ('Engineer D', 'yellow'), (' (Grav 68)', 'fg'),
                 (' has high influence but low robust survival (', 'fg_dim'), ('12', 'red'), (')', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch3-data-warning.svg'))


def ch3_data_team_metrics():
    c = CodeCardSVG('data', width=440, label='Classification')
    c.add_spans([('Structure: ', 'fg_dim'), ('Architectural Team', 'purple'), (' (0.34)', 'fg_dim')])
    c.add_spans([('Culture:   ', 'fg_dim'), ('Builder', 'green'), (' (0.40)', 'fg_dim')])
    c.add_spans([('Phase:     ', 'fg_dim'), ('Mature', 'green'), (' (1.00)', 'fg_dim')])
    c.add_spans([('Risk:      ', 'fg_dim'), ('Healthy', 'green'), (' (0.30)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch3-data-team-metrics.svg'))


def ch3_data_pattern():
    c = CodeCardSVG('data', width=480, label='Pattern')
    c.add_spans([('Producer', 'yellow'), (' + ', 'fg_dim'), ('High Gravity', 'purple'), (' + ', 'fg_dim'), ('Low Robust', 'red')])
    c.save(os.path.join(IMG_DIR, 'ch3-data-pattern.svg'))


def ch3_data_anchor_mass():
    c = CodeCardSVG('data', width=240, label='Pattern')
    c.add_spans([('Anchor', 'blue'), (' + ', 'fg_dim'), ('Mass', 'yellow')])
    c.save(os.path.join(IMG_DIR, 'ch3-data-anchor-mass.svg'))


def ch3_diagram_be_evolution():
    c = CodeCardSVG('diagram', width=360, label='Evolution')
    c.add_spans([('Producer', 'yellow')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Anchor', 'blue')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Inheritance Architect', 'purple')])
    c.save(os.path.join(IMG_DIR, 'ch3-diagram-be-evolution.svg'))


def ch3_diagram_fe_evolution():
    c = CodeCardSVG('diagram', width=360, label='Evolution')
    c.add_spans([('Producer', 'yellow')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('High-Gravity Producer', 'yellow')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Emergent Architect', 'purple')])
    c.save(os.path.join(IMG_DIR, 'ch3-diagram-fe-evolution.svg'))


# ── Chapter 4 Code Cards ──

def ch4_data_engineer_f():
    c = CodeCardSVG('data', width=720, label='Profile')
    c.add_spans([('Engineer F', 'yellow', True), ('  —  ', 'fg_dim'),
                 ('Prod ', 'fg_dim'), ('93', 'purple'), (' | ', 'fg_dim'),
                 ('Qual ', 'fg_dim'), ('75', 'green'), (' | ', 'fg_dim'),
                 ('Robust ', 'fg_dim'), ('36', 'fg'), (' | ', 'fg_dim'),
                 ('Design ', 'fg_dim'), ('47', 'yellow'), (' | ', 'fg_dim'),
                 ('Total ', 'fg_dim'), ('55.5', 'yellow', True)])
    c.add_spans([('Role: ', 'fg_dim'), ('Anchor (0.87)', 'blue'), (' | ', 'fg_dim'),
                 ('Style: ', 'fg_dim'), ('Resilient (0.66)', 'blue'), (' | ', 'fg_dim'),
                 ('State: ', 'fg_dim'), ('Former (0.73)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-engineer-f.svg'))


def ch4_data_phase_risk():
    c = CodeCardSVG('data', width=380, label='Classification')
    c.add_spans([('Phase: ', 'fg_dim'), ('Legacy-Heavy', 'yellow'), (' (0.67)', 'fg_dim')])
    c.add_spans([('Risk:  ', 'fg_dim'), ('Talent Drain', 'red'), (' (0.43)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-phase-risk.svg'))


def ch4_data_debt_avg():
    c = CodeCardSVG('data', width=360, label='Averages')
    c.add_spans([('Team Averages:', 'fg_dim')])
    c.add_spans([('  Debt Cleanup   ', 'fg'), ('47.0', 'yellow')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-debt-avg.svg'))


def ch4_diagram_fe_evolution():
    """Same as ch3 FE evolution."""
    ch3_diagram_fe_evolution()  # Reuses the same SVG


def ch4_diagram_be_evolution():
    """Same as ch3 BE evolution."""
    ch3_diagram_be_evolution()  # Reuses the same SVG


def ch4_data_design_pattern():
    c = CodeCardSVG('data', width=440, label='Pattern')
    c.add_spans([('Domain', 'purple'), (' + ', 'fg_dim'), ('Application', 'blue'), (' + ', 'fg_dim'), ('UseCase', 'aqua')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-design-pattern.svg'))


def ch4_data_role_count():
    c = CodeCardSVG('data', width=260, label='Roles')
    c.add_spans([('Architect  ', 'fg_dim'), ('1', 'purple')])
    c.add_spans([('Anchor     ', 'fg_dim'), ('3', 'blue')])
    c.add_spans([('Producer   ', 'fg_dim'), ('0', 'red')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-role-count.svg'))


def ch4_diagram_producer_vacuum():
    c = CodeCardSVG('diagram', width=320, label='Structure')
    c.add_spans([('Architect', 'purple')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Anchor', 'blue')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Production Vacuum', 'red')])
    c.save(os.path.join(IMG_DIR, 'ch4-diagram-producer-vacuum.svg'))


def ch4_diagram_three_layer():
    c = CodeCardSVG('diagram', width=280, label='Structure')
    c.add_spans([('Architect', 'purple')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Anchor', 'blue')])
    c.add_line('↓', color='fg_dim')
    c.add_spans([('Producer', 'yellow')])
    c.save(os.path.join(IMG_DIR, 'ch4-diagram-three-layer.svg'))


def ch4_data_bus_factor():
    c = CodeCardSVG('data', width=560, label='Warning')
    c.add_spans([('Top contributor (', 'fg'), ('machuz', 'yellow'), (') accounts for ', 'fg'), ('46%', 'red', True), (' of core production', 'fg')])
    c.add_spans([('ProdDensity drops to ', 'fg'), ('39', 'red'), (' without them', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-bus-factor.svg'))


def ch4_data_elite():
    c = CodeCardSVG('data', width=260, label='Character')
    c.add_spans([('★ ', 'yellow'), ('Elite', 'purple', True), (' (1.00)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch4-data-elite.svg'))


# ── Chapter 5 Code Cards ──

def ch5_bash_timeline():
    c = CodeCardSVG('bash', width=660)
    c.add_line('# Default: last 4 quarters in 3-month spans', color='fg_dim')
    c.add_spans([('eis', 'green'), (' timeline --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# From 2024, quarterly', color='fg_dim')
    c.add_spans([('eis', 'green'), (' timeline --span 3m --since 2024-01-01 --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# Half-year spans, full history', color='fg_dim')
    c.add_spans([('eis', 'green'), (' timeline --span 6m --periods 0 --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# Specific members only', color='fg_dim')
    c.add_spans([('eis', 'green'), (' timeline --author alice,bob --recursive ~/workspace', 'fg')])
    c.add_blank()
    c.add_line('# JSON output', color='fg_dim')
    c.add_spans([('eis', 'green'), (' timeline --format json --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch5-bash-timeline.svg'))


def ch5_data_role_transitions():
    c = CodeCardSVG('data', width=720, label='Transitions')
    c.add_spans([
        ('Architect', 'purple'), (' → ', 'fg_dim'), ('Anchor', 'blue'), (' → ', 'fg_dim'),
        ('Architect', 'purple'), (' → ', 'fg_dim'), ('Producer', 'yellow'), (' → ', 'fg_dim'),
        ('Producer', 'yellow'), (' → ', 'fg_dim'), ('Producer', 'yellow'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch5-data-role-transitions.svg'))


def ch5_data_hesitation():
    c = CodeCardSVG('data', width=820, label='Timeline')
    c.add_spans([('Period         ', 'fg_dim'), ('Total', 'fg_dim'), ('  Prod', 'fg_dim'), ('  Qual', 'fg_dim'),
                 ('  Surv', 'fg_dim'), ('  Design', 'fg_dim'), ('  Role', 'fg_dim'), ('        Style', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2025-Q2 (Apr)  ', 'fg'), ('73.2', 'yellow'), ('    67', 'green'), ('    91', 'purple'),
                 ('   100', 'purple'), ('     100', 'purple'), ('  Architect', 'purple'), ('    Builder', 'green')])
    c.add_spans([('2025-Q3 (Jul)  ', 'fg'), ('72.4', 'yellow'), ('    73', 'green'), ('    97', 'purple'),
                 ('   100', 'purple'), ('      73', 'green'), ('  Anchor', 'blue'), ('       Balanced', 'blue'),
                 ('  ← here', 'yellow')])
    c.add_spans([('2025-Q4 (Oct)  ', 'fg'), ('81.7', 'purple'), ('   100', 'purple'), ('    68', 'green'),
                 ('   100', 'purple'), ('     100', 'purple'), ('  Architect', 'purple'), ('    Balanced', 'blue')])
    c.save(os.path.join(IMG_DIR, 'ch5-data-hesitation.svg'))


def ch5_data_new_universe():
    c = CodeCardSVG('data', width=700, label='Per-Repo')
    c.add_spans([('Quarter  ', 'fg_dim'), ('Repo A (existing)', 'fg_dim'), ('  Repo B (existing)', 'fg_dim'), ('  Repo C (new)', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2025-Q4  ', 'fg'), ('       5', 'fg_dim'), ('                 5', 'fg_dim'),
                 ('         ', 'fg'), ('1,352', 'yellow', True), ('  ← here', 'yellow')])
    c.save(os.path.join(IMG_DIR, 'ch5-data-new-universe.svg'))


def ch5_data_transition():
    c = CodeCardSVG('data', width=820, label='Timeline')
    c.add_spans([('Period         ', 'fg_dim'), ('Total', 'fg_dim'), ('  Prod', 'fg_dim'), ('  Qual', 'fg_dim'),
                 ('  Surv', 'fg_dim'), ('  Design', 'fg_dim'), ('  Role', 'fg_dim'), ('        Style', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2025-Q3 (Jul)  ', 'fg'), ('72.4', 'yellow'), ('    73', 'green'), ('    97', 'purple'),
                 ('   100', 'purple'), ('      73', 'green'), ('  Anchor', 'blue'), ('       Balanced', 'blue'),
                 ('  ← producing', 'fg_dim')])
    c.add_spans([('2025-Q4 (Oct)  ', 'fg'), ('81.7', 'purple'), ('   100', 'purple'), ('    68', 'green'),
                 ('   100', 'purple'), ('     100', 'purple'), ('  Architect', 'purple'), ('    Balanced', 'blue'),
                 ('  ← creating', 'yellow')])
    c.save(os.path.join(IMG_DIR, 'ch5-data-transition.svg'))


def ch5_data_return():
    c = CodeCardSVG('data', width=860, label='Timeline')
    c.add_spans([('Period         ', 'fg_dim'), ('Total', 'fg_dim'), ('  Prod', 'fg_dim'), ('  Qual', 'fg_dim'),
                 ('  Surv', 'fg_dim'), ('  Design', 'fg_dim'), ('  Role', 'fg_dim'), ('        Style', 'fg_dim'),
                 ('      State', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2025-Q4 (Oct)  ', 'fg'), ('81.7', 'purple'), ('   100', 'purple'), ('    68', 'green'),
                 ('   100', 'purple'), ('     100', 'purple'), ('  Architect', 'purple'), ('    Balanced', 'blue')])
    c.add_spans([('2026-Q1 (Jan)  ', 'fg'), ('78.1', 'green'), ('   100', 'purple'), ('    84', 'purple'),
                 ('    83', 'purple'), ('     100', 'purple'), ('  Anchor', 'blue'), ('       Builder', 'green'),
                 ('      Active', 'green')])
    c.save(os.path.join(IMG_DIR, 'ch5-data-return.svg'))


def ch5_bash_timeline_author():
    c = CodeCardSVG('bash', width=540)
    c.add_spans([('eis', 'green'), (' timeline --author alice --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch5-bash-timeline-author.svg'))


# ── Chapter 6 Code Cards ──

def ch6_data_architect_quarter():
    c = CodeCardSVG('data', width=520, label='Timeline')
    c.add_spans([('Period   ', 'fg_dim'), ('Total', 'fg_dim'), ('  Role', 'fg_dim'), ('       Style', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2024-Q3  ', 'fg'), ('56.1', 'yellow'), ('  Anchor', 'blue'), ('     Balanced', 'blue')])
    c.add_spans([('2024-Q4  ', 'fg'), ('75.7', 'green'), ('  Architect', 'purple'), ('  Balanced', 'blue')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-architect-quarter.svg'))


def ch6_data_simultaneous():
    c = CodeCardSVG('data', width=780, label='Timeline')
    c.add_spans([('Period   ', 'fg_dim'), ('Engineer I', 'fg_dim'), ('           ', 'fg'),
                 ('Engineer J', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2025-Q2  ', 'fg'), ('73.2', 'yellow'), ('  ', 'fg'), ('Architect', 'purple'),
                 ('    ', 'fg'), ('63.8', 'green'), ('  ', 'fg'), ('Architect', 'purple')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-simultaneous.svg'))


def ch6_data_engineer_j_transitions():
    c = CodeCardSVG('data', width=720, label='Transitions')
    c.add_spans([
        ('Architect', 'purple'), (' → ', 'fg_dim'), ('Anchor', 'blue'), (' → ', 'fg_dim'),
        ('Architect', 'purple'), (' → ', 'fg_dim'), ('Producer', 'yellow'), (' → ', 'fg_dim'),
        ('Producer', 'yellow'), (' → ', 'fg_dim'), ('Producer', 'yellow'),
    ])
    c.save(os.path.join(IMG_DIR, 'ch6-data-engineer-j-transitions.svg'))


def ch6_data_health():
    c = CodeCardSVG('data', width=340, label='Health')
    c.add_spans([('Growth Potential: ', 'fg'), ('20.0', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-health.svg'))


def ch6_data_producer_vacuum():
    c = CodeCardSVG('data', width=360, label='Classification')
    c.add_spans([('Character: ', 'fg_dim'), ('Balanced', 'blue')])
    c.add_spans([('Phase:     ', 'fg_dim'), ('Declining', 'red')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-producer-vacuum.svg'))


def ch6_data_effective_members():
    c = CodeCardSVG('data', width=360, label='Classification')
    c.add_spans([('Effective Members: ', 'fg_dim'), ('5', 'green')])
    c.add_spans([('Total:             ', 'fg_dim'), ('48.3', 'yellow'), (' (average)', 'fg_dim')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-effective-members.svg'))


def ch6_data_machuz_phases():
    c = CodeCardSVG('data', width=560, label='Timeline')
    c.add_spans([('Period   ', 'fg_dim'), ('Total', 'fg_dim'), ('  Role', 'fg_dim'), ('       Style', 'fg_dim')])
    c.add_separator()
    c.add_spans([('2024-H2  ', 'fg'), ('76.4', 'green'), ('  Anchor', 'blue'), ('     Builder', 'green')])
    c.add_spans([('2025-H1  ', 'fg'), ('58.4', 'yellow'), ('  Producer', 'yellow'), ('   Balanced', 'blue')])
    c.add_spans([('2025-H2  ', 'fg'), ('92.5', 'purple'), ('  Architect', 'purple'), ('  Builder', 'green')])
    c.save(os.path.join(IMG_DIR, 'ch6-data-machuz-phases.svg'))


def ch6_bash_timeline_cmd():
    c = CodeCardSVG('bash', width=620)
    c.add_spans([('eis', 'green'), (' timeline --span 6m --periods 0 --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch6-bash-timeline.svg'))


def ch6_data_decline_model():
    """Reuse same decline diagram as ch2 — same content."""
    pass  # ch2_diagram_decline already generates this


# ── Chapter 7 Code Cards ──

def ch7_bash_html():
    c = CodeCardSVG('bash', width=700)
    c.add_spans([('eis', 'green'), (' timeline --format html --output timeline.html --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch7-bash-html.svg'))


# ── Chapter 8 Code Cards ──

def ch8_bash_per_repo():
    c = CodeCardSVG('bash', width=540)
    c.add_spans([('eis', 'green'), (' analyze --recursive --per-repo ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch8-bash-per-repo.svg'))


def ch8_bash_timeline_cmd():
    c = CodeCardSVG('bash', width=620)
    c.add_spans([('eis', 'green'), (' timeline --span 6m --periods 0 --recursive ~/workspace', 'fg')])
    c.save(os.path.join(IMG_DIR, 'ch8-bash-timeline.svg'))


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating blog SVGs...")

    # Chapter 1
    ch1_backend_table()
    ch1_frontend_table()

    # Chapter 2
    ch2_warnings()

    # Chapter 3
    ch3_engineer_profiles()
    ch3_producer_warning()

    # Chapter 4
    ch4_backend_team()
    ch4_team_classification()
    ch4_structure()

    # Chapter 5
    ch5_engineer_f_timeline()
    ch5_engineer_j_timeline()
    ch5_engineer_i_timeline()
    ch5_per_repo_commits()
    ch5_transitions()
    ch5_comparison_table()
    ch5_team_timeline()

    # Chapter 6
    ch6_backend_team_timeline()
    ch6_backend_score_averages()
    ch6_frontend_team_timeline()
    ch6_infra_firmware()
    ch6_machuz_timeline()
    ch6_be_architects()
    ch6_fe_architects()
    ch6_engineer_k()
    ch6_gravity_transfer()
    ch6_evolution_paths()
    ch6_evolution_model()

    # Chapter 7
    ch7_team_classification()

    # Chapter 8
    ch8_repo_scores()
    ch8_structure_comparison()
    ch8_per_repo_breakdown()

    # Cover images
    cover_image(1, "Measuring Engineering Impact", "from Git History Alone", cover_ch1_visual)
    cover_image(2, "Beyond Individual Scores", "Measuring Team Health from Git History", cover_ch2_visual)
    cover_image(3, "Two Paths to Architect", "How Engineers Evolve Differently", cover_ch3_visual)
    cover_image(4, "Backend Architects Converge", "The Sacred Work of Laying Souls to Rest", cover_ch4_visual)
    cover_image(5, "Timeline: Scores Don't Lie", "And They Capture Hesitation Too", cover_ch5_visual)
    cover_image(6, "Teams Evolve", "The Laws of Organization Revealed by Timelines", cover_ch6_visual)
    cover_image(7, "Observing the Universe of Code", "Four Forces, Gravity, and Seasoned Design", cover_ch7_visual)
    cover_image(8, "Engineering Relativity", "Why the Same Engineer Gets Different Scores", cover_ch8_visual)

    # ═══ Code Card SVGs ═══
    print("\n  Generating code card SVGs...")

    # ── Chapter 1 ──
    ch1_formula_production()
    ch1_formula_quality()
    ch1_code_survival()
    ch1_code_debt()
    ch1_code_indispensability()
    ch1_formula_total()
    ch1_formula_gravity()
    ch1_formula_gravity_health()
    ch1_bash_install()
    ch1_bash_usage()
    # JA-only
    ch1_bash_gitlog()
    ch1_code_fixdetect()
    ch1_yaml_config()

    # ── Chapter 2 ──
    ch2_bash_team()
    ch2_yaml_teams()
    ch2_formula_complementarity()
    ch2_formula_growth()
    ch2_formula_sustainability()
    ch2_formula_productivity()
    ch2_formula_quality_consistency()
    ch2_formula_weight()
    ch2_diagram_growth_model()
    ch2_diagram_decline()
    ch2_bash_install_team()
    # JA-only
    ch2_formula_debt_balance()
    ch2_formula_risk_ratio()

    # ── Chapter 3 ──
    ch3_gravity_calc_d()
    ch3_gravity_calc_a()
    ch3_data_warning()
    ch3_data_team_metrics()
    ch3_data_pattern()
    ch3_data_anchor_mass()
    ch3_diagram_be_evolution()
    ch3_diagram_fe_evolution()

    # ── Chapter 4 ──
    ch4_data_engineer_f()
    ch4_data_phase_risk()
    ch4_data_debt_avg()
    ch4_diagram_fe_evolution()
    ch4_diagram_be_evolution()
    ch4_data_design_pattern()
    ch4_data_role_count()
    ch4_diagram_producer_vacuum()
    ch4_diagram_three_layer()
    ch4_data_bus_factor()
    ch4_data_elite()

    # ── Chapter 5 ──
    ch5_bash_timeline()
    ch5_data_role_transitions()
    ch5_data_hesitation()
    ch5_data_new_universe()
    ch5_data_transition()
    ch5_data_return()
    ch5_bash_timeline_author()

    # ── Chapter 6 ──
    ch6_data_architect_quarter()
    ch6_data_simultaneous()
    ch6_data_engineer_j_transitions()
    ch6_data_health()
    ch6_data_producer_vacuum()
    ch6_data_effective_members()
    ch6_data_machuz_phases()
    ch6_bash_timeline_cmd()
    ch6_data_decline_model()

    # ── Chapter 7 ──
    ch7_bash_html()

    # ── Chapter 8 ──
    ch8_bash_per_repo()
    ch8_bash_timeline_cmd()

    print(f"\nDone! Generated SVGs in {IMG_DIR}")

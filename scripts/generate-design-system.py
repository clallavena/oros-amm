import re, math, sys

css = open(sys.argv[1], encoding="utf-8").read()
out = sys.argv[2]

# ---------- lecture des primitives OKLCH ----------
prims = {}
ORIG = {}  # valeur telle qu'écrite dans global.css, ex. "oklch(42.3% 0.065 162)"
for name, L, C, H in re.findall(r"--color-([\w-]+):\s*oklch\(([\d.]+)%\s+([\d.]+)\s+([\d.]+)\)", css):
    prims[name] = (float(L) / 100, float(C), float(H))
    ORIG[name] = f"oklch({L}% {C} {H})"

def oklch_to_rgb(L, C, H):
    a = C * math.cos(math.radians(H)); b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    def enc(x):
        x = max(0, min(1, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return [round(enc(v) * 255) for v in (r, g, bl)]

HEX = {k: "#%02x%02x%02x" % tuple(oklch_to_rgb(*v)) for k, v in prims.items()}
HEX["white"] = "#ffffff"

def lum(h):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

# ---------- rôles par thème (miroir de global.css) ----------
THEMES = [
    ("Forêt", "forest", "forest", "forest", "lime-400", "stone-500", "forest-500"),
    ("Neige", "snow", "glacier", "glacier", "ice-300", "glacier-stone-500", "glacier-500"),
    ("Crépuscule", "sunset", "dusk", "dusk", "apricot-400", "dusk-stone-500", "dusk-600"),
]
def roles(scale, accent, muted, hero):
    return dict(
        primary=HEX[f"{scale}-500"], hover=HEX[f"{scale}-600"], hero=HEX[hero],
        light=HEX[f"{scale}-300"], onmuted=HEX[f"{scale}-200"],
        secondary=HEX[accent], onsecondary=HEX[f"{scale}-800"],
        bg=HEX[f"{scale}-50"], text=HEX[f"{scale}-700"], muted=HEX[muted],
        border=HEX[f"{scale}-200"], strong=HEX[f"{scale}-400"],
    )

F = roles("forest", "lime-400", "stone-500", "forest-500")
HEAD = "Epilogue, Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
BODY = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

W = 1200
s = []
def add(x): s.append(x)
def t(x, y, txt, size=14, fill=None, weight=400, family=BODY, anchor="start", extra=""):
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill or F["text"]}" text-anchor="{anchor}" {extra}>{txt}</text>')

def label(x, y, txt):  # « eyebrow » du SectionTitle
    t(x, y, txt.upper(), 12, F["primary"], 600, BODY, extra='letter-spacing="2.4"')

def button(x, y, txt, variant, R, w=None):
    w = w or (len(txt) * 7.6 + 48)
    h = 40
    if variant == "primary": bg, fg, st = R["primary"], "#ffffff", None
    elif variant == "secondary": bg, fg, st = R["secondary"], R["onsecondary"], None
    elif variant == "ghost": bg, fg, st = "none", R["primary"], R["primary"]
    else: bg, fg, st = "#ffffff", R["primary"], None
    stroke = f' stroke="{st}" stroke-width="1"' if st else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{bg}"{stroke}/>')
    t(x + w / 2, y + 25, txt, 14, fg, 600, anchor="middle")
    return w

# ================= EN-TÊTE =================
y = 0
add(f'<rect x="0" y="0" width="{W}" height="150" fill="{F["hero"]}"/>')
# silhouette de crêtes, discrète
add(f'<path d="M0 150 L140 92 L210 120 L330 58 L420 104 L520 76 L640 122 L760 70 L860 108 L980 52 L1080 98 L1200 80 L1200 150 Z" fill="{F["hover"]}" opacity="0.55"/>')
t(48, 58, "Design System", 12, F["secondary"], 600, extra='letter-spacing="2.4"')
t(48, 100, "Oros", 44, "#ffffff", 700, HEAD, extra='letter-spacing="-0.5"')
t(160, 100, "— jetons, thèmes &amp; composants", 22, F["onmuted"], 600, HEAD)
t(48, 128, "Tailwind CSS 4 · @theme · couleurs OKLCH · source : src/styles/global.css", 13, F["onmuted"])

# ================= 1. ÉCHELLE FORÊT =================
y = 196
label(48, y, "01 · Primitives")
t(48, y + 30, "Échelle forêt — teinte fixe 162°, seule la clarté L varie", 22, F["text"], 700, HEAD)
t(1152, y + 30, "hex sRGB (converti) · oklch(L C H) d'origine", 12, F["muted"], 400, MONO, "end")
steps = [50, 100, 200, 300, 400, 500, 600, 700, 800]
sw, gap, x0, top = 112, 12, 48, y + 52
for i, st in enumerate(steps):
    k = f"forest-{st}"; hx = HEX[k]; L = prims[k][0] * 100
    x = x0 + i * (sw + gap)
    add(f'<rect x="{x}" y="{top}" width="{sw}" height="84" rx="12" fill="{hx}" stroke="{F["border"]}" stroke-width="1"/>')
    fg = "#ffffff" if lum(hx) < 0.18 else F["text"]
    t(x + 12, top + 26, str(st), 15, fg, 700)
    if st == 500: t(x + sw - 12, top + 26, "primary", 11, F["secondary"], 600, anchor="end")
    t(x + 12, top + 74, f"L {L:.1f}%", 11, fg, 400, MONO)
    t(x, top + 106, hx, 12, F["text"], 400, MONO)
    L_, C_, H_ = ORIG[k][6:-1].split()  # "oklch(98% 0.012 162)" -> "98%", "0.012", "162"
    t(x, top + 122, f"{L_} {C_} {H_}", 10.5, F["muted"], 400, MONO)

# accents & états
y2 = top + 156
t(48, y2, "Accents &amp; états", 15, F["text"], 600, HEAD)
acc = [("lime-400", "secondary"), ("stone-500", "text-muted"), ("meadow-600", "success"),
       ("clay-500", "danger"), ("forest-700", "focus")]
for i, (k, role) in enumerate(acc):
    x = 48 + i * 224
    add(f'<rect x="{x}" y="{y2 + 16}" width="44" height="44" rx="22" fill="{HEX[k]}"/>')
    t(x + 56, y2 + 34, role, 14, F["text"], 600)
    t(x + 56, y2 + 52, f"{k} · {HEX[k]}", 12, F["muted"], 400, MONO)
    t(x + 56, y2 + 68, ORIG[k], 11, F["muted"], 400, MONO)

# ================= 2. THÈMES =================
y = y2 + 128
label(48, y, "02 · Thèmes d'univers")
t(48, y + 30, "Même clarté L par cran : seuls la teinte et le chroma changent", 22, F["text"], 700, HEAD)
t(48, y + 54, "Les composants ne lisent que des rôles (primary, secondary, text…), redéfinis par [data-theme].", 14, F["muted"])
cw, ch, cy = 352, 352, y + 76
for i, (nom, key, scale, _, accent, muted, hero) in enumerate(THEMES):
    R = roles(scale, accent, muted, hero)
    x = 48 + i * (cw + 24)
    add(f'<g><clipPath id="c{i}"><rect x="{x}" y="{cy}" width="{cw}" height="{ch}" rx="16"/></clipPath>')
    add(f'<rect x="{x}" y="{cy}" width="{cw}" height="{ch}" rx="16" fill="{R["bg"]}" stroke="{R["border"]}"/>')
    add(f'<g clip-path="url(#c{i})">')
    add(f'<rect x="{x}" y="{cy}" width="{cw}" height="112" fill="{R["hero"]}"/>')
    add(f'<path d="M{x} {cy+112} l70 -38 l40 22 l70 -44 l60 34 l50 -20 l62 32 l0 14 Z" fill="{R["hover"] if key!="sunset" else R["primary"]}" opacity="0.6"/>')
    add('</g></g>')
    t(x + 20, cy + 32, f'data-theme="{key}"', 12, R["onmuted"], 400, MONO)
    t(x + 20, cy + 66, nom, 26, "#ffffff", 700, HEAD)
    # échelle compacte
    for j, st in enumerate(steps):
        add(f'<rect x="{x + 20 + j * 34.6}" y="{cy + 128}" width="32" height="20" rx="4" fill="{HEX[f"{scale}-{st}"]}" stroke="{R["border"]}" stroke-width="0.5"/>')
    t(x + 20, cy + 178, "Titre de sortie", 18, R["text"], 700, HEAD)
    t(x + 20, cy + 200, "Texte secondaire d'une carte", 13, R["muted"])
    bw = button(x + 20, cy + 220, "Réserver", "primary", R)
    button(x + 20 + bw + 10, cy + 220, "Contact", "secondary", R)
    button(x + 20, cy + 272, "Découvrir", "ghost", R)
    # ratios
    r1 = ratio(R["text"], R["bg"]); r2 = ratio("#ffffff", R["primary"]); r3 = ratio(R["onsecondary"], R["secondary"])
    t(x + 20, cy + 336, f"contraste  texte {r1:.1f}  ·  blanc/primary {r2:.1f}  ·  CTA {r3:.1f}", 10.5, R["muted"], 400, MONO)

# ================= 3. TYPOGRAPHIE =================
y = cy + ch + 56
label(48, y, "03 · Typographie")
t(48, y + 30, "Epilogue pour les titres, Inter pour le texte", 22, F["text"], 700, HEAD)
ty = y + 64
add(f'<rect x="48" y="{ty}" width="1104" height="232" rx="16" fill="#ffffff" stroke="{F["border"]}"/>')
rows = [
    ("eyebrow", "Inter 600 · 14 · capitales · tracking-widest", "LOREM IPSUM", 14, F["primary"], 600, BODY, 'letter-spacing="2.8"'),
    ("h2", "Epilogue 700 · 36–30 · tracking-tight", "Lorem ipsum dolor sit amet", 32, F["text"], 700, HEAD, 'letter-spacing="-0.6"'),
    ("h3", "Epilogue 600 · 20", "Lorem ipsum dolor sit amet", 20, F["text"], 600, HEAD, ""),
    ("body-lg", "Inter 400 · 18 · leading-relaxed", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus et dui justo. ", 18, F["muted"], 400, BODY, ""),
]
for i, (tag, spec, sample, size, fill, wgt, fam, ex) in enumerate(rows):
    ry = ty + 44 + i * 48
    t(72, ry, tag, 12, F["primary"], 600, MONO)
    t(72, ry + 16, spec, 10.5, F["muted"], 400, MONO)
    t(360, ry + 6, sample, size, fill, wgt, fam, extra=ex)

# ================= 4. COMPOSANTS =================
y = ty + 232 + 56
label(48, y, "04 · Composants")
t(48, y + 30, "Button — 4 variantes, rounded-full, anneau de focus double", 22, F["text"], 700, HEAD)
by = y + 56
add(f'<rect x="48" y="{by}" width="740" height="196" rx="16" fill="#ffffff" stroke="{F["border"]}"/>')
bx = 72
for v, txt in [("primary", "primary"), ("secondary", "secondary"), ("ghost", "ghost")]:
    w = button(bx, by + 28, txt, v, F, 128)
    t(bx + 64, by + 90, f'variant="{v}"', 10.5, F["muted"], 400, MONO, "middle")
    bx += 148
# light sur fond hero
add(f'<rect x="{bx - 8}" y="{by + 16}" width="152" height="88" rx="12" fill="{F["hero"]}"/>')
button(bx + 4, by + 28, "light", "light", F, 128)
t(bx + 68, by + 90, 'variant="light"', 10.5, F["onmuted"], 400, MONO, "middle")
# focus
fx, fy = 72, by + 124
add(f'<rect x="{fx - 6}" y="{fy - 6}" width="176" height="52" rx="26" fill="none" stroke="{F["text"]}" stroke-width="2"/>')
add(f'<rect x="{fx - 2}" y="{fy - 2}" width="168" height="44" rx="22" fill="none" stroke="#ffffff" stroke-width="2"/>')
button(fx, fy, "focus-visible", "primary", F, 164)
t(fx + 196, fy + 18, "Contour foncé (focus) + liseré blanc : visible sur fond clair", 12, F["muted"])
t(fx + 196, fy + 34, "comme sur fond vert — WCAG 2.2, technique C40.", 12, F["muted"])

# carte
cx, cyy = 812, by
add(f'<rect x="{cx}" y="{cyy}" width="340" height="196" rx="16" fill="#ffffff" stroke="{F["border"]}"/>')
add(f'<clipPath id="card"><rect x="{cx}" y="{cyy}" width="340" height="196" rx="16"/></clipPath>')
add(f'<rect x="{cx}" y="{cyy}" width="340" height="86" fill="{F["light"]}" clip-path="url(#card)"/>')
add(f'<path d="M{cx} {cyy+86} l60 -30 l40 18 l70 -40 l60 30 l50 -16 l60 26 l0 12 Z" fill="{F["strong"]}" opacity="0.7" clip-path="url(#card)"/>')
t(cx + 20, cyy + 116, "Card", 18, F["text"], 600, HEAD)
t(cx + 20, cyy + 140, "rounded-2xl · border · bg-surface", 13, F["muted"])
t(cx + 20, cyy + 172, "Découvrir →", 14, F["primary"], 600)

H = by + 196 + 48
t(W / 2, H - 16, "Généré depuis src/styles/global.css — valeurs hex converties depuis OKLCH (sRGB), ratios WCAG 2.x calculés.", 11, F["muted"], 400, BODY, "middle")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
       f'aria-labelledby="ds-title ds-desc">\n<title id="ds-title">Design System Oros</title>\n'
       f'<desc id="ds-desc">Échelle de couleurs forêt, accents et états, trois thèmes d\'univers (Forêt, Neige, Crépuscule), '
       f'typographie Epilogue et Inter, composants Button et Card.</desc>\n'
       f'<rect width="{W}" height="{H}" fill="{F["bg"]}"/>\n' + "\n".join(s) + "\n</svg>\n")
open(out, "w", encoding="utf-8").write(svg)

# ================= VARIABLES FIGMA (format DTCG) =================
# Spécification : https://www.designtokens.org/tr/drafts/format/ (W3C Design Tokens CG)
# Deux collections, à importer dans cet ordre dans le panneau Variables de Figma :
#   1. Primitives : toutes les couleurs brutes (forest/500, lime/400…), un seul mode ;
#   2. Rôles : primary, text… un fichier par mode (forest, snow, sunset),
#      chaque rôle étant un alias vers une primitive, comme var(--color-…) dans le CSS.
import json, os

# Nom EXACT de la collection des primitives dans Figma : les alias des rôles la retrouvent par ce nom.
PRIMITIVES_COLLECTION = "Primitives"

figma_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(out) or ".", "figma")
os.makedirs(figma_dir, exist_ok=True)

def block(selector_regex):
    """Contenu entre accolades du premier bloc dont l'en-tête correspond à la regex."""
    m = re.search(selector_regex + r"\s*\{", css)
    if not m:
        return ""
    depth, i = 1, m.end()
    while depth:
        depth += {"{": 1, "}": -1}.get(css[i], 0)
        i += 1
    return css[m.end():i - 1]

def aliases(body):
    """--color-ROLE: var(--color-PRIM)  ->  {ROLE: PRIM}"""
    return dict(re.findall(r"--color-([\w-]+):\s*var\(--color-([\w-]+)\)", body))

def split_name(name):
    """forest-500 -> ("forest", "500") ; glacier-stone-500 -> ("glacier-stone", "500") ; white -> (None, "white")"""
    group, _, step = name.rpartition("-")
    return (group, step) if step.isdigit() else (None, name)

def color_value(hx):
    """Valeur couleur DTCG en sRGB : Figma ne travaille qu'en sRGB / Display P3, pas en OKLCH."""
    comps = [round(int(hx[i:i + 2], 16) / 255, 4) for i in (1, 3, 5)]
    return {"colorSpace": "srgb", "components": comps, "alpha": 1, "hex": hx}

# --- primitives : oklch() lues plus haut + couleurs hex (white, black) ---
for name, hx in re.findall(r"--color-([\w-]+):\s*(#[0-9a-fA-F]{3,6})\s*;", css):
    hx = hx.lower()
    if len(hx) == 4:
        hx = "#" + "".join(c * 2 for c in hx[1:])
    HEX[name] = hx
    ORIG.setdefault(name, hx)

primitives = {}
for name in HEX:
    if name not in ORIG:
        continue
    group, step = split_name(name)
    token = {"$type": "color", "$value": color_value(HEX[name]),
             "$description": f"Source : {ORIG[name]} (global.css)",
             "$extensions": {"com.figma": {"codeSyntax": {"WEB": f"var(--color-{name})"}}}}
    (primitives.setdefault(group, {}) if group else primitives)[step] = token

def figma_name(prim):
    """forest-500 -> "forest/500" : nom de la variable dans Figma (les groupes JSON deviennent des « / »)."""
    group, step = split_name(prim)
    return f"{group}/{step}" if group else step

def role_token(role, prim):
    """Alias vers une primitive d'une AUTRE collection.
    La référence DTCG "{forest.500}" n'est résolue par Figma qu'à l'intérieur du fichier importé
    (erreur token-with-invalid-reference sinon). Pour viser une autre collection, Figma lit
    $extensions.com.figma.aliasData ; $value porte la couleur résolue, ce qui donne au moins
    la bonne couleur si l'alias n'est pas retrouvé."""
    return {"$type": "color", "$value": color_value(HEX[prim]),
            "$extensions": {"com.figma.aliasData": {"targetVariableName": figma_name(prim),
                                                     "targetVariableSetName": PRIMITIVES_COLLECTION},
                            "com.figma": {"codeSyntax": {"WEB": f"var(--color-{role})"}}}}

# --- rôles : défauts de @theme, surchargés par chaque [data-theme] ---
defaults = aliases(block(r"@theme"))
themes = {key: aliases(block(rf'\[data-theme="{key}"\]'))
          for key in re.findall(r'\[data-theme="([\w-]+)"\]\s*\{', css)}

files = {"primitives.tokens.json": primitives}
for key, overrides in themes.items():
    mode = {**defaults, **overrides}  # surface, danger, success, focus restent ceux de @theme
    files[f"roles.{key}.tokens.json"] = {role: role_token(role, prim) for role, prim in mode.items()}

for fname, data in files.items():
    with open(os.path.join(figma_dir, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
print(f"Variables Figma : {len(files)} fichiers dans {figma_dir}")
for nom, key, scale, _, accent, muted, hero in THEMES:
    R = roles(scale, accent, muted, hero)
    print(nom, "text/bg %.2f" % ratio(R["text"], R["bg"]), "muted/bg %.2f" % ratio(R["muted"], R["bg"]),
          "white/primary %.2f" % ratio("#ffffff", R["primary"]), "cta %.2f" % ratio(R["onsecondary"], R["secondary"]))
print(HEX["forest-500"], HEX["glacier-500"], HEX["dusk-500"], HEX["meadow-600"])

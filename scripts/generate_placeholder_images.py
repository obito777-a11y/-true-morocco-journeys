#!/usr/bin/env python3
"""
generate_placeholder_images.py

Regenerates every placeholder photo used across the True Morocco Journeys
site (hero banners, tour/destination cards, blog thumbnails, team avatars,
and the logo). Useful if you tweak the brand palette and want the
placeholder photography to match before you swap in real photography.

Requires: pip install pillow numpy --break-system-packages
Run from anywhere — output always goes to ../images relative to this file.
"""
import os, math, random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(7)
np.random.seed(7)

BASE = str((Path(__file__).resolve().parent.parent / "images"))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG  = os.path.join(FONT_DIR, "DejaVuSans.ttf")
if not os.path.exists(F_BOLD):
    print("Note: DejaVu fonts not found on this system — falling back to a "
          "bundled default font. Label text may look plainer. On Debian/"
          "Ubuntu, `apt-get install fonts-dejavu` for the original look.")
    F_BOLD = F_REG = None  # PIL will fall back to its built-in bitmap font

# ---------------------------------------------------------------- palette --
C = {
    'rust':        (204, 85, 0),
    'rust_dark':   (138, 58, 8),
    'rust_light':  (230, 126, 60),
    'teal':        (0, 77, 64),
    'teal_dark':   (0, 48, 40),
    'teal_light':  (0, 120, 100),
    'navy':        (26, 34, 56),
    'navy_dark':   (15, 20, 34),
    'gold':        (212, 168, 67),
    'gold_light':  (236, 205, 135),
    'sand':        (214, 175, 117),
    'sand_dark':   (163, 122, 71),
    'sand_light':  (243, 224, 190),
    'white':       (255, 255, 255),
    'blue':        (43, 96, 156),
    'blue_dark':   (24, 56, 97),
    'blue_light':  (120, 170, 214),
    'blue_pale':   (180, 210, 232),
}

def font(path, size):
    if path is None:
        return ImageFont.load_default()
    return ImageFont.truetype(path, size)

# --------------------------------------------------------- gradient maker --
def gradient(size, stops, angle='diag'):
    """stops: list of (pos 0..1, (r,g,b)). angle: 'diag' | 'vert' | 'horiz'"""
    w, h = size
    xx, yy = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    if angle == 'diag':
        t = (xx + yy) / 2
    elif angle == 'vert':
        t = yy
    else:
        t = xx
    out = np.zeros((h, w, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        mask = (t >= p0) & (t <= p1 + 1e-6)
        local = np.clip((t - p0) / max(p1 - p0, 1e-6), 0, 1)
        for ch in range(3):
            layer = c0[ch] + (c1[ch] - c0[ch]) * local
            out[..., ch] = np.where(mask, layer, out[..., ch])
    return Image.fromarray(out.astype(np.uint8), 'RGB')

# -------------------------------------------------------------- textures --
def star8(draw, cx, cy, r_outer, r_inner, color, width=1, fill=None):
    pts = []
    for i in range(16):
        ang = math.pi / 8 * i - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    if fill:
        draw.polygon(pts, fill=fill)
    else:
        draw.polygon(pts, outline=color, width=width)

def scatter_zellige(img, color, density=42, alpha=16):
    """Faint repeating 8-point star motif across the whole image."""
    w, h = img.size
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    step = max(int(w / density), 36)
    for y in range(-step, h + step, step):
        offset = step // 2 if (y // step) % 2 else 0
        for x in range(-step, w + step, step + offset % step + 1):
            xx = x + offset
            star8(d, xx, y, step * 0.30, step * 0.13, color + (alpha,), width=2)
    img.paste(Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB'), (0, 0))
    return img

def vignette(img, strength=0.40):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    dist2 = ((xx - cx) / (w / 1.15)) ** 2 + ((yy - cy) / (h / 1.15)) ** 2
    mask = np.exp(-strength * dist2)          # smooth Gaussian falloff, no hard edge
    mask = (1 - strength * 0.9) + strength * 0.9 * mask
    arr = np.array(img).astype(np.float32)
    for ch in range(3):
        arr[..., ch] *= mask
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def grain(img, amount=6):
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-amount, amount + 1, arr.shape[:2])
    for ch in range(3):
        arr[..., ch] = np.clip(arr[..., ch] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

# ----------------------------------------------------- motif silhouettes --
def soft_sun(draw_img, cx, cy, r, color):
    """Paint a soft-glow sun directly onto an RGBA image via alpha compositing."""
    glow = Image.new('RGBA', draw_img.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for i in range(10, 0, -1):
        a = int(14 * (1 - i/10) + 4)
        rr = r * (1 + i*0.22)
        gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=color+(a,))
    gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color+(255,))
    return Image.alpha_composite(draw_img, glow)

def draw_dunes(draw, w, h, base_color):
    warm_mid = C['sand_dark']
    warm_dark = C['rust_dark']
    layers = [(0.55, lerp(base_color, warm_mid, 0.55)),
              (0.70, lerp(base_color, warm_dark, 0.55)),
              (0.85, lerp(base_color, warm_dark, 0.78))]
    for frac, col in layers:
        y0 = int(h * frac)
        pts = [(0, h)]
        n = 6
        for i in range(n + 1):
            x = w * i / n
            wob = math.sin(i * 1.7 + frac * 9) * h * 0.05
            pts.append((x, y0 + wob))
        pts.append((w, h))
        draw.polygon(pts, fill=col)

def draw_medina_skyline(draw, w, h, base_color, with_minaret=True):
    ground = int(h * 0.62)
    dark = lerp(base_color, (0,0,0), 0.55)
    darker = lerp(base_color, (0,0,0), 0.72)
    # back wall crenellations
    draw.rectangle([0, ground, w, h], fill=dark)
    step = w // 22
    for x in range(0, w, step):
        draw.rectangle([x, ground - step*0.55, x + step*0.6, ground], fill=dark)
    # domes
    n_domes = 5
    for i in range(n_domes):
        cx = w * (0.12 + i * 0.18)
        rad = w * 0.045
        topY = ground - rad*1.5
        draw.pieslice([cx-rad, topY-rad, cx+rad, topY+rad], 180, 360, fill=darker)
        draw.rectangle([cx-rad, topY, cx+rad, ground], fill=darker)
    if with_minaret:
        mx = w * 0.62
        mw = w * 0.05
        mtop = ground - h * 0.42
        draw.rectangle([mx-mw, mtop, mx+mw, ground], fill=darker)
        draw.rectangle([mx-mw*1.35, mtop, mx+mw*1.35, mtop+h*0.045], fill=darker)
        draw.polygon([(mx-mw*1.1, mtop), (mx+mw*1.1, mtop), (mx, mtop-h*0.06)], fill=darker)
        for fy in [mtop+h*0.10, mtop+h*0.20, mtop+h*0.30]:
            draw.rectangle([mx-mw*0.35, fy, mx+mw*0.35, fy+h*0.03], fill=lerp(darker,(255,255,255),0.15))

def draw_mountains(draw, w, h, base_color):
    layers = [(0.45, lerp(base_color, (255,255,255), 0.18)),
              (0.60, lerp(base_color, (0,0,0), 0.18)),
              (0.78, lerp(base_color, (0,0,0), 0.40))]
    rng = random.Random(3)
    for frac, col in layers:
        y0 = int(h * frac)
        pts = [(0, h)]
        x = 0
        peakn = 5
        for i in range(peakn + 1):
            x = w * i / peakn
            peak = y0 - rng.uniform(0.05, 0.22) * h
            pts.append((x, peak))
        pts.append((w, h))
        draw.polygon(pts, fill=col)
    # snow caps on the front-most (already drawn) - add light triangles on back layer for realism
def draw_coast(draw, w, h, base_color):
    ground = int(h * 0.68)
    draw.rectangle([0, ground, w, h], fill=lerp(base_color, (0,0,0), 0.25))
    for i, frac in enumerate([0.70, 0.78, 0.86, 0.94]):
        y = int(h * frac)
        col = lerp(base_color, (255,255,255), 0.25 + i*0.05)
        pts = [(0, y)]
        for xi in range(0, 11):
            x = w * xi / 10
            wob = math.sin(xi * 1.3 + i) * h * 0.012
            pts.append((x, y + wob))
        pts += [(w, h), (0, h)]
        draw.polygon(pts, fill=col)

def draw_bluecity(draw, w, h, base_color):
    rows, cols = 4, 9
    cw, ch_ = w / cols, h / rows * 1.15
    rng = random.Random(11)
    for r in range(rows):
        for cidx in range(cols):
            x0 = cidx * cw
            y0 = h - (r+1) * (h/rows)
            shade = lerp(base_color, (255,255,255), rng.uniform(0.0, 0.30))
            draw.rectangle([x0, y0, x0+cw-4, y0 + h/rows - 4], fill=shade)
            # arched doorway
            aw = cw * 0.42
            ax = x0 + cw/2
            ay = y0 + h/rows - 8
            ah = h/rows * 0.55
            arch_col = lerp(shade, (0,0,0), 0.35)
            draw.rectangle([ax-aw/2, ay-ah, ax+aw/2, ay], fill=arch_col)
            draw.pieslice([ax-aw/2, ay-ah-aw/2, ax+aw/2, ay-ah+aw/2], 180, 360, fill=arch_col)

def draw_single_arch(draw, w, h, base_color, line_color):
    cx = w/2
    aw, ah = w*0.46, h*0.66
    top = h*0.16
    bottom = h*0.96
    left, right = cx-aw/2, cx+aw/2
    pts = [(left, bottom), (left, top+ah*0.42)]
    steps = 30
    for i in range(steps+1):
        ang = math.pi*(1 - i/steps)
        x = cx + (aw/2)*math.cos(ang)
        y = (top+ah*0.42) - (ah*0.42)*math.sin(ang)
        pts.append((x,y))
    pts.append((right, bottom))
    draw.polygon(pts, fill=lerp(base_color,(0,0,0),0.3))
    draw.line(pts+[pts[0]], fill=line_color, width=5, joint='curve')

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

# -------------------------------------------------------------- label UI --
def add_label_bar(img, title, subtitle, accent=C['rust']):
    w, h = img.size
    bar_h = max(int(h*0.16), 64)
    overlay = Image.new('RGBA', (w,h), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([0, h-bar_h, w, h], fill=(15,20,34,185))
    d.rectangle([0, h-bar_h, int(w*0.012)+6, h], fill=accent+(255,))
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    d2 = ImageDraw.Draw(img)
    title_size = max(int(bar_h*0.34), 16)
    sub_size = max(int(bar_h*0.20), 11)
    pad = int(w*0.025)+14
    fb = font(F_BOLD, title_size)
    fr = font(F_REG, sub_size)
    d2.text((pad, h-bar_h+bar_h*0.16), title.upper(), font=fb, fill=(255,255,255,255))
    d2.text((pad, h-bar_h+bar_h*0.58), subtitle, font=fr, fill=(212,168,67,255))
    return img.convert('RGB')

# ------------------------------------------------------------- the maker --
THEMES = {
    'dunes':    dict(grad=[(0,C['gold_light']),(0.45,C['sand']),(1,C['rust_dark'])], draw=draw_dunes, sun=(0.80,0.28,0.13)),
    'medina':   dict(grad=[(0,C['rust_light']),(0.5,C['rust']),(1,C['navy_dark'])], draw=lambda d,w,h,c: draw_medina_skyline(d,w,h,c,True)),
    'medina2':  dict(grad=[(0,C['gold_light']),(0.5,C['rust']),(1,C['navy_dark'])], draw=lambda d,w,h,c: draw_medina_skyline(d,w,h,c,False)),
    'mosque':   dict(grad=[(0,(110,80,120)),(0.45,C['rust']),(1,C['navy_dark'])], draw=lambda d,w,h,c: draw_medina_skyline(d,w,h,c,True)),
    'mountains':dict(grad=[(0,C['blue_pale']),(0.5,C['teal_light']),(1,C['navy_dark'])], draw=draw_mountains),
    'coast':    dict(grad=[(0,C['blue_pale']),(0.45,C['blue']),(1,C['blue_dark'])], draw=draw_coast, sun=(0.16,0.24,0.09)),
    'bluecity': dict(grad=[(0,C['blue_pale']),(0.5,C['blue']),(1,C['blue_dark'])], draw=draw_bluecity),
    'arch':     dict(grad=[(0,C['gold_light']),(0.5,C['rust']),(1,C['teal_dark'])], draw=lambda d,w,h,c: draw_single_arch(d,w,h,c,C['gold_light'])),
}

def make_image(path, size, theme, title, subtitle, label=True, accent=None):
    w, h = size
    th = THEMES[theme]
    img = gradient(size, th['grad'], angle='diag')
    overlay = Image.new('RGBA', size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    base_color = th['grad'][1][1]
    th['draw'](d, w, h, base_color)
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    if 'sun' in th:
        sx, sy, sr = th['sun']
        img = soft_sun(img, w*sx, h*sy, h*sr, C['gold_light'])
    img = img.convert('RGB')
    img = scatter_zellige(img, C['white'], density=24, alpha=10)
    img = vignette(img, strength=0.40)
    img = grain(img, amount=4)
    if label:
        img = add_label_bar(img, title, subtitle, accent or C['rust'])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, quality=87)
    print("wrote", path, size)

def make_portrait_avatar(path, size, bg, initials):
    img = Image.new('RGB', size, bg)
    d = ImageDraw.Draw(img)
    w,h = size
    # subtle radial
    img = gradient(size, [(0,lerp(bg,(255,255,255),0.12)),(1,lerp(bg,(0,0,0),0.18))], angle='diag')
    d = ImageDraw.Draw(img)
    f = font(F_BOLD, int(h*0.34))
    bbox = d.textbbox((0,0), initials, font=f)
    tw, th_ = bbox[2]-bbox[0], bbox[3]-bbox[1]
    d.text(((w-tw)/2 - bbox[0], (h-th_)/2 - bbox[1]), initials, font=f, fill=(255,255,255))
    # simple person silhouette ring
    d.ellipse([w*0.5-w*0.46,h*0.5-h*0.46,w*0.5+w*0.46,h*0.5+h*0.46], outline=(255,255,255,60), width=3)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, quality=88)
    print("wrote", path)

def make_logo():
    size=(360,360)
    img = Image.new('RGBA', size, (0,0,0,0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0]/2, size[1]/2
    col = C['rust']
    # outer keyhole arch
    aw, ah = 230, 260
    left, right = cx-aw/2, cx+aw/2
    top = cy-ah/2
    bottom = cy+ah/2
    pts = [(left,bottom)]
    steps=40
    for i in range(steps+1):
        ang = math.pi*(1-i/steps)
        x = cx + (aw/2)*math.cos(ang)
        y = (top+ah*0.30) - (ah*0.30)*math.sin(ang)
        pts.append((x,y))
    pts.append((right,bottom))
    pts.append((left,bottom))
    d.line(pts, fill=col, width=9, joint='curve')
    # inner mountains
    mtop = cy-10
    d.line([(cx-70,cy+70),(cx-25,mtop),(cx+18,cy+25),(cx+70,cy+70)], fill=col, width=8, joint='curve')
    d.line([(cx-25,mtop),(cx-25,mtop)], fill=col, width=8)
    # sun
    d.ellipse([cx+35,cy-55,cx+65,cy-25], outline=col, width=6)
    # camel-ish simple mark (humps) bottom
    d.line([(cx-58,cy+78),(cx-40,cy+58),(cx-25,cy+72),(cx-8,cy+55),(cx+8,cy+78)], fill=col, width=6, joint='curve')
    img.save(f"{BASE}/logo.png")
    # favicon
    fav = img.resize((64,64), Image.LANCZOS)
    fav.save(f"{BASE}/favicon.png")
    print("wrote logo + favicon")

# ============================================================ run it all ==
if __name__ == "__main__":
    make_logo()

    # HERO banners
    make_image(f"{BASE}/hero/hero-home.jpg", (1920,950), 'mosque',
               "Hassan II Mosque", "Casablanca, at golden hour — replace with licensed photography")
    make_image(f"{BASE}/hero/hero-tours.jpg", (1920,560), 'dunes',
               "Sahara Desert Expeditions", "Erg Chebbi dunes, Merzouga")
    make_image(f"{BASE}/hero/hero-destinations.jpg", (1920,560), 'medina',
               "Medinas & Imperial Cities", "Marrakesh, Fes, Rabat & beyond")
    make_image(f"{BASE}/hero/hero-about.jpg", (1920,560), 'mountains',
               "Our Journey Since 2012", "High Atlas Mountains")
    make_image(f"{BASE}/hero/hero-blog.jpg", (1920,560), 'medina2',
               "Stories From The Road", "Field notes from our guides")
    make_image(f"{BASE}/hero/hero-contact.jpg", (1920,560), 'arch',
               "Let's Plan Your Journey", "Riad courtyard, Marrakesh")
    make_image(f"{BASE}/hero/hero-tour-detail.jpg", (1920,720), 'dunes',
               "Sahara Desert 4x4 Expedition", "3 Days / 2 Nights — Merzouga")
    make_image(f"{BASE}/og-image.jpg", (1200,630), 'mosque',
               "True Morocco Journeys", "Unforgettable 4x4 journeys & luxury glamping")

    # TOURS
    tours = [
        ("sahara-4x4", 'dunes', "Sahara Desert 4x4 Expedition", "Merzouga dunes"),
        ("marrakesh-cultural", 'medina', "Marrakesh Cultural Immersion", "Medina & souks"),
        ("atlas-trek", 'mountains', "Atlas Mountains Trekking", "Toubkal foothills"),
        ("chefchaouen-blue", 'bluecity', "Chefchaouen Blue City Tour", "The blue pearl"),
        ("fes-imperial", 'medina2', "Fes Imperial City Discovery", "Tanneries & madrasas"),
        ("agadir-coastal", 'coast', "Agadir Coastal Escape", "Atlantic coastline"),
        ("essaouira-day", 'coast', "Essaouira Day Trip", "Fishing port & ramparts"),
        ("desert-glamping", 'dunes', "Luxury Desert Glamping", "Erg Chigaga camp"),
        ("casablanca-city", 'mosque', "Casablanca City Highlights", "Modern imperial city"),
        ("rabat-imperial", 'medina2', "Rabat Imperial History", "Kasbah & mausoleum"),
        ("ouarzazate-kasbahs", 'dunes', "Ouarzazate Kasbah Trail", "Ait Benhaddou"),
        ("merzouga-stars", 'dunes', "Merzouga Stargazing Camp", "Bivouac under the stars"),
    ]
    for slug, theme, title, sub in tours:
        make_image(f"{BASE}/tours/{slug}.jpg", (900,680), theme, title, sub)

    # DESTINATIONS
    dests = [
        ("marrakesh", 'medina', "Marrakesh", "The Red City"),
        ("casablanca", 'mosque', "Casablanca", "Economic capital"),
        ("fes", 'medina2', "Fes", "Oldest imperial city"),
        ("rabat", 'medina2', "Rabat", "Capital of Morocco"),
        ("chefchaouen", 'bluecity', "Chefchaouen", "The Blue Pearl"),
        ("agadir", 'coast', "Agadir", "Atlantic resort city"),
        ("essaouira", 'coast', "Essaouira", "Windswept port town"),
        ("sahara", 'dunes', "Sahara Desert", "Erg Chebbi & Erg Chigaga"),
        ("atlas-mountains", 'mountains', "Atlas Mountains", "Berber villages & peaks"),
    ]
    for slug, theme, title, sub in dests:
        make_image(f"{BASE}/destinations/{slug}.jpg", (900,680), theme, title, sub)

    # ABOUT
    make_image(f"{BASE}/about-story.jpg", (900,760), 'medina',
               "Our Story", "Founded by Moroccan guides, 2012")
    make_image(f"{BASE}/about-mission.jpg", (900,600), 'mountains',
               "Our Mission", "Sustainable, authentic travel")

    # BLOG
    blogs = [
        ("blog-1", 'dunes', "Best Time to Visit the Sahara", "Seasonal guide"),
        ("blog-2", 'medina', "10 Things to Do in Marrakesh", "City guide"),
        ("blog-3", 'bluecity', "A Guide to Chefchaouen", "The blue pearl"),
        ("blog-4", 'medina2', "A Taste of Moroccan Cuisine", "Food & culture"),
        ("blog-5", 'mountains', "Packing for the Atlas Mountains", "Trekking tips"),
        ("blog-6", 'coast', "Sustainable Travel in Morocco", "Travel responsibly"),
    ]
    for slug, theme, title, sub in blogs:
        make_image(f"{BASE}/blog/{slug}.jpg", (900,620), theme, title, sub)

    # GALLERY (square, no label bar for clean instagram-style grid)
    gallery = [
        ("gallery-1", 'dunes'), ("gallery-2", 'medina'), ("gallery-3", 'bluecity'),
        ("gallery-4", 'coast'), ("gallery-5", 'mountains'), ("gallery-6", 'mosque'),
    ]
    for slug, theme in gallery:
        make_image(f"{BASE}/gallery/{slug}.jpg", (700,700), theme, "", "", label=False)

    # TEAM avatars
    team = [
        ("team-1", C['teal'], "YB"),
        ("team-2", C['rust'], "SK"),
        ("team-3", C['navy'], "HA"),
        ("team-4", C['teal_dark'], "ML"),
    ]
    for slug, bg, initials in team:
        make_portrait_avatar(f"{BASE}/team/{slug}.jpg", (500,500), bg, initials)

    # TESTIMONIAL avatars
    testi = [("avatar-1", C['rust'], "JM"), ("avatar-2", C['teal'], "EP"), ("avatar-3", C['navy'], "RT")]
    for slug, bg, initials in testi:
        make_portrait_avatar(f"{BASE}/team/{slug}.jpg", (160,160), bg, initials)

    print("ALL DONE")

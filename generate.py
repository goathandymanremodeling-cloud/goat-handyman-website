#!/usr/bin/env python3
"""
GOAT Handyman & Remodeling - Static Site Generator
Run: python3 generate.py
Generates all pages from site.config.json + templates
"""

import json, os, re, shutil

# ── Load config ───────────────────────────────────────────
with open("site.config.json", encoding="utf-8") as f:
    cfg = json.load(f)

# Critical (above-the-fold) CSS, inlined in every page so the first paint does
# not wait for the stylesheets. Regenerate with extract_critical.py whenever
# main.css / builders-design.css / theme.css change.
with open("css/critical.css", encoding="utf-8") as f:
    CRITICAL_CSS = f.read()

B = cfg["brand"]
SERVICES = cfg["services"]
AREAS = cfg["serviceAreas"]
REVIEWS = cfg["reviews"]
FAQS = cfg["faqs"]
GALLERY = cfg.get("gallery", [])

PHONE = B["phone"]
PHONE_RAW = B["phoneRaw"]
NAME = B["name"]
ADDRESS = f"{B['address']}, {B['city']}, {B['state']} {B['zip']}"
PRIMARY = B["primaryColor"]
SECONDARY = B["secondaryColor"]
WEBHOOK = B["zapierWebhook"]
FONT    = B.get("font", "Inter")
BASE    = B.get("baseUrl", "")  # For subdirectory hosting (e.g., "/goat-preview")

# ── Lucide icon helpers ───────────────────────────────────
def _svg(paths, size=16):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
            f' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
            f' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
            f' aria-hidden="true">{paths}</svg>')

ICON = {
    'phone':    _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>"),
    'pin':      _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>"),
    'clock':    _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>"),
    'star':     _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>"),
    'shield':   _svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>"),
    'home':     _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>"),
    'dollar':   _svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>"),
    'check':    _svg("<polyline points='20 6 9 17 4 12'/>"),
    'check-circle': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>"),
    'clipboard':_svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>"),
    'camera':   _svg("<path d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z'/><circle cx='12' cy='13' r='3'/>"),
    'timer':    _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>"),
    'ruler':    _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>"),
    'phone_lg': _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>", 24),
    'pin_lg':   _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>", 24),
    'clock_lg': _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>", 24),
    'timer_lg': _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>", 24),
    'star_lg':  _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>", 20),
    'dollar_lg':_svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>", 24),
    'ruler_lg': _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>", 24),
    'home_lg':  _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>", 24),
    'shield_lg':_svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>", 24),
    'clipboard_lg': _svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>", 24),
    'check_lg': _svg("<polyline points='20 6 9 17 4 12'/>", 20),
    'check-circle_lg': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>", 24),
}
# ─────────────────────────────────────────────────────────

# ── Gallery mapping: service slug → gallery folder name ───
GALLERY_MAP = {
    "bathroom-remodeling": "bathroom",
    "carpentry": "carpentry",
    "deck-repair": "deck",
    "door-repair": "door",
    "drywall-repair": "drywall",
    "flooring": "flooring",
    "handyman-services": "handyman",
    "home-repair": "home-repair",
    "insulation": "insulation",
    "kitchen-remodeling": "kitchen",
    "plumbing-electrical": "plumbing",
    "siding": "siding",
    "window-repair": "window",
}

def get_gallery_photos(service_slug):
    """Get list of gallery photos for a service. Returns list of (src, alt) tuples."""
    folder = GALLERY_MAP.get(service_slug)
    if not folder:
        return []

    gallery_dir = f"images/gallery/{folder}"
    if not os.path.isdir(gallery_dir):
        return []

    photos = []
    for f in sorted(os.listdir(gallery_dir)):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            photos.append((f"{BASE}/images/gallery/{folder}/{f}", f"{folder.title()} project photo"))
    return photos

def service_gallery(service_slug, service_name):
    """Generate gallery HTML for a service page with lazy loading and responsive images."""
    photos = get_gallery_photos(service_slug)
    if not photos:
        return ""

    gallery_items = "\n".join(f'''
      <div class="gallery-item">
        <img src="{src}" alt="{alt}" loading="lazy" width="400" height="300" decoding="async" />
      </div>''' for src, alt in photos)

    return f'''
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Work</span>
      <h2>{service_name} Projects</h2>
    </div>
    <div class="gallery-grid">
      {gallery_items}
    </div>
  </div>
</section>
'''

pages_created = []
pages_failed = []

# ── Helpers ───────────────────────────────────────────────

def make_theme_css():
    primary_dark   = B.get("primaryDark", B["primaryColor"])
    secondary_dark = B.get("secondaryDark", B["secondaryColor"])
    accent         = B.get("accentColor", "")
    accent_line    = f"  --accent:       {accent};\n  --accent-dark:  {accent};" if accent else ""
    content = f"""/* Auto-generated by generate.py - do not edit manually */
:root {{
  --green:        {B["primaryColor"]};
  --green-dark:   {primary_dark};
  --green-light:  {B["secondaryColor"]};
  --green-hover:  {secondary_dark};
{accent_line}
}}
"""
    write("css/theme.css", content)

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write(path, content):
    d = os.path.dirname(path)
    if d:
        mkdir(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    pages_created.append(path.replace(os.getcwd() + "/", ""))

def nav(active=""):
    service_links = "\n".join(
        f'<li><a href="{BASE}/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(
        f'<a href="{BASE}/services/{s["slug"]}/">{s["name"]}</a>'
        for s in SERVICES
    )
    return f"""
<header class="site-header">
  <nav class="main-nav" aria-label="Main navigation">
    <div class="container nav-inner">
      <a href="{BASE}/" class="nav-logo">
        <img src="{BASE}/images/logo.png" alt="{NAME} logo" width="83" height="96" />
      </a>
      <ul class="nav-links">
        <li class="has-dropdown">
          <a href="{BASE}/services/" class="{'active' if active=='services' else ''}">Services ▾</a>
          <ul class="dropdown">
            <li><span class="dropdown-label">Our Services</span></li>
            {service_links}
            <li><a href="{BASE}/services/" class="dropdown-all">View All Services →</a></li>
          </ul>
        </li>
        <li><a href="{BASE}/about/" class="{'active' if active=='about' else ''}">About Us</a></li>
        <li><a href="{BASE}/service-areas/" class="{'active' if active=='areas' else ''}">Service Areas</a></li>
        <li><a href="{BASE}/reviews/" class="{'active' if active=='reviews' else ''}">Reviews</a></li>
        <li><a href="{BASE}/faq/" class="{'active' if active=='faq' else ''}">FAQ</a></li>
      </ul>
      <div class="nav-cta">
        <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
        <a href="{BASE}/request-service" class="btn btn-primary btn-sm">Get Started</a>
      </div>
      <button class="hamburger" id="hamburger" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</header>
<div class="mobile-menu" id="mobile-menu">
  <div class="mobile-menu-header">
    <img src="{BASE}/images/logo.png" alt="{NAME}" width="35" height="40" />
    <button id="mobile-close" aria-label="Close">✕</button>
  </div>
  <a href="{BASE}/request-service" class="btn btn-primary mobile-cta">Get Free Estimate</a>
  <a href="tel:{PHONE_RAW}" class="btn btn-outline mobile-cta">{PHONE}</a>
  <button class="mobile-services-toggle" onclick="this.classList.toggle('open');this.nextElementSibling.classList.toggle('open');">
    Services <span class="toggle-icon">▼</span>
  </button>
  <div class="mobile-services-list">
    {mobile_service_links}
    <a href="{BASE}/services/">View All Services →</a>
  </div>
  <a href="{BASE}/about/">About Us</a>
  <a href="{BASE}/service-areas/">Service Areas</a>
  <a href="{BASE}/reviews/">Reviews</a>
  <a href="{BASE}/faq/">FAQ</a>
</div>"""

def footer():
    service_links = "\n".join(
        f'<li><a href="{BASE}/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    # Show first 12 areas split into two columns
    areas_col1 = AREAS[:6]
    areas_col2 = AREAS[6:12]
    areas1_links = "\n".join(f'<li><a href="{BASE}/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in areas_col1)
    areas2_links = "\n".join(f'<li><a href="{BASE}/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in areas_col2)

    # Social links (only show if configured)
    social_html = ""
    if B.get('facebook') or B.get('instagram'):
        social_links = ""
        if B.get('facebook'):
            social_links += f'''<a href="{B['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
          </a>'''
        if B.get('instagram'):
            social_links += f'''<a href="{B['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
          </a>'''
        social_html = f'<div class="footer-social">{social_links}</div>'

    return f"""
<footer class="site-footer">
  <div class="footer-main">
    <div class="container footer-grid">
      <div class="footer-brand">
        <a href="{BASE}/"><img src="{BASE}/images/logo.png" alt="{NAME}" width="62" height="72" class="footer-logo" /></a>
        <p>{B.get('footerTagline', f"{NAME} - locally based in {B['city']}, NY.")}</p>
        <a href="tel:{PHONE_RAW}" class="footer-phone">{PHONE}</a>
        <p class="footer-address">{ADDRESS}</p>
        {social_html}
      </div>
      <div class="footer-col">
        <h3>Our Services</h3>
        <ul>{service_links}</ul>
      </div>
      <div class="footer-col">
        <h3>Service Areas</h3>
        <ul>{areas1_links}<li><a href="{BASE}/service-areas/">All Areas →</a></li></ul>
      </div>
      <div class="footer-col">
        <h3>More Areas</h3>
        <ul>{areas2_links}<li><a href="{BASE}/service-areas/">All Areas →</a></li></ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <span>&copy; <span id="yr"></span> {NAME}. All rights reserved.</span>
      <div class="footer-legal">
        <a href="{BASE}/privacy-policy">Privacy Policy</a>
        <a href="{BASE}/terms">Terms of Use</a>
        <a href="{BASE}/accessibility">Accessibility</a>
      </div>
    </div>
  </div>
</footer>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="{BASE}/js/main.js" defer></script>"""

def head(title, desc, canonical, schema="", extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  {GA4_TAG}
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  {extra_head}
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="https://{B['domain']}{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://{B['domain']}{canonical}" />
  <meta property="og:image" content="{BASE}/images/hero-bg.jpg" />
  <meta name="robots" content="index, follow" />
  <link rel="icon" href="{BASE}/images/logo.png" type="image/png" />
  <link rel="apple-touch-icon" href="{BASE}/images/logo.png" />
  <link rel="sitemap" type="application/xml" href="{BASE}/sitemap.xml" />
  {schema}
  <link rel="preload" as="font" type="font/woff2" href="{BASE}/fonts/inter-latin.woff2" crossorigin />
  <link rel="preload" as="font" type="font/woff2" href="{BASE}/fonts/outfit-latin.woff2" crossorigin />
  <style>{FONTS_FACE}
{CRITICAL_CSS}</style>
  <link rel="preload" as="style" href="{BASE}/css/main.css?v=4" onload="this.onload=null;this.rel='stylesheet'" />
  <link rel="preload" as="style" href="{BASE}/css/theme.css?v=2" onload="this.onload=null;this.rel='stylesheet'" />
  <link rel="preload" as="style" href="{BASE}/css/builders-design.css?v=2" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="{BASE}/css/main.css?v=4" /><link rel="stylesheet" href="{BASE}/css/theme.css?v=2" /><link rel="stylesheet" href="{BASE}/css/builders-design.css?v=2" /></noscript>
</head>
<body>"""

def booking_form(compact=False):
    service_opts = "\n".join(
        f'<option value="{s["slug"]}">{s["name"]}</option>'
        for s in SERVICES
    )
    if compact:
        return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Get Your Custom Quote</h3>
    <p>Response within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Your full name" /></div>
    <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
    <div class="form-group"><label>Service</label>
      <select name="service" aria-label="Select a service"><option value="">Select a service...</option>{service_opts}</select>
    </div>
    <div class="form-group"><label>Details</label><textarea name="message" rows="3" placeholder="Tell us about your project..."></textarea></div>
    <input type="text" name="_honey" style="display:none" />
    <input type="hidden" name="_next" value="https://www.goathandymanremodeling.com/thank-you" />
    <input type="hidden" name="_captcha" value="false" />
    <button type="submit" class="btn btn-primary btn-block">Send Request →</button>
  </form>
</div>"""
    return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Request a Free Estimate</h3>
    <p>We respond within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-row">
      <div class="form-group"><label>First Name *</label><input type="text" name="first_name" required placeholder="John" /></div>
      <div class="form-group"><label>Last Name *</label><input type="text" name="last_name" required placeholder="Smith" /></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
      <div class="form-group"><label>City *</label><input type="text" name="city" required placeholder="e.g., Garden City" /></div>
    </div>
    <div class="form-group"><label>Email</label><input type="email" name="email" placeholder="you@email.com" /></div>
    <div class="form-group"><label>Service Needed *</label>
      <select name="service" required aria-label="Select a service"><option value="">Select a service...</option>{service_opts}<option value="other">Other / Not Sure</option></select>
    </div>
    <div class="form-group"><label>Project Details</label><textarea name="message" rows="4" placeholder="Describe your project, property size, timeline..."></textarea></div>
    <input type="text" name="_honey" style="display:none" />
    <input type="hidden" name="_subject" value="New Estimate Request - {NAME}" />
    <input type="hidden" name="_next" value="https://www.goathandymanremodeling.com/thank-you" />
    <input type="hidden" name="_captcha" value="false" />
    <button type="submit" class="btn btn-primary btn-block">Send My Request →</button>
    <p class="form-disclaimer">We respect your privacy. No spam, ever.</p>
  </form>
</div>"""

# Google "G" logo (multicolour) + the business's Google profile link, used to
# make the on-site reviews read as real Google reviews.
GOOGLE_G = """<svg class="google-g" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="#4285F4" d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82z"/><path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96H1.29v3.09C3.26 21.3 7.31 24 12 24z"/><path fill="#FBBC05" d="M5.27 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.38l3.98-3.09z"/><path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.62l3.98 3.09C6.22 6.86 8.87 4.75 12 4.75z"/></svg>"""
GOOGLE_REVIEWS_URL = "https://share.google/N2PxdQLDACAWKNpIu"
GA4_TAG = """<script async src="https://www.googletagmanager.com/gtm.js?id=G-VNESQG0KJ9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
</script>"""
FONTS_FACE = """@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:optional;src:url(/fonts/inter-latin.woff2) format('woff2');}
@font-face{font-family:'Outfit';font-style:normal;font-weight:100 900;font-display:optional;src:url(/fonts/outfit-latin.woff2) format('woff2');}"""
_AVATAR_COLORS = ["#1565C0", "#c62828", "#2e7d32", "#5e35b1", "#007c91", "#bf360c", "#3949ab", "#00695c"]  # all >= 4.5:1 with white initials (WCAG AA)
_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def _avatar_color(name):
    return _AVATAR_COLORS[sum(name.encode()) % len(_AVATAR_COLORS)]

def _review_month(iso_date):
    y, m, _d = iso_date.split("-")
    return f"{_MONTHS[int(m) - 1]} {y}"

def review_cards(city=None):
    """Generate review cards styled like real Google reviews: coloured initial
    avatar, reviewer name + review month, stars, text, and a 'Posted on
    Google' footer with the Google logo."""
    cards = []
    for r in REVIEWS:
        stars = ICON["star"] * r["rating"]
        parts = r["name"].split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        color = _avatar_color(r["name"])
        when = _review_month(r.get("date", "2025-01-01"))
        cards.append(f"""
    <div class="review-card google-review">
      <div class="review-header">
        <div class="review-avatar" style="background:{color}">{initials}</div>
        <div class="review-header-text">
          <div class="review-author">{r['name']}</div>
          <div class="review-date">{when}</div>
        </div>
      </div>
      <div class="review-stars">{stars}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-source">Posted on {GOOGLE_G} <span>Google</span></div>
    </div>""")
    return "\n".join(cards)

def service_area_links():
    return "\n".join(
        f'<a href="{BASE}/service-areas/{a["slug"]}/" class="city-pill">{a["name"]}</a>'
        for a in AREAS
    )

def breadcrumbs(crumbs):
    items = []
    schema_items = []
    for i, (label, url) in enumerate(crumbs):
        # Prepend BASE to URLs that start with /
        display_url = url
        if url and url.startswith("/") and not url.startswith(BASE):
            display_url = BASE + url
        if url:
            items.append(f'<li><a href="{display_url}">{label}</a></li>')
        else:
            items.append(f'<li>{label}</li>')
        if url:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}","item":"https://{B["domain"]}{url}"}}')
        else:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}"}}')
    schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(schema_items)}]}}
  </script>"""
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="container"><ol class="breadcrumb-list">{"".join(items)}</ol></div></nav>', schema

# Build sameAs array (only include non-empty social links)
_same_as = [s for s in [B.get('facebook',''), B.get('instagram','')] if s]
_same_as_json = f',"sameAs":{json.dumps(_same_as)}' if _same_as else ''

# Build reviews array with datePublished
_reviews_json = json.dumps([{
    "@type": "Review",
    "author": {"@type": "Person", "name": r["name"]},
    "datePublished": r.get("date", "2025-01-01"),
    "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"},
    "reviewBody": r["text"]
} for r in REVIEWS])

# Build aggregateRating
_avg_rating = sum(r["rating"] for r in REVIEWS) / len(REVIEWS) if REVIEWS else 5
_aggregate_rating = json.dumps({
    "@type": "AggregateRating",
    "ratingValue": str(round(_avg_rating, 1)),
    "reviewCount": str(len(REVIEWS)),
    "bestRating": "5",
    "worstRating": "1"
})

LOCAL_BIZ_SCHEMA = f"""<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME}",
    "url":"https://{B['domain']}/",
    "telephone":"{PHONE}",
    "address":{{"@type":"PostalAddress","streetAddress":"{B['address']}","addressLocality":"{B['city']}","addressRegion":"{B['state']}","postalCode":"{B['zip']}","addressCountry":"US"}},
    "priceRange":"$$",
    "openingHours":"Su-Fr 08:00-18:00",
    "geo":{{"@type":"GeoCoordinates","latitude":40.7065,"longitude":-73.6212}},
    "areaServed":{json.dumps([{"@type":"City","name":a["name"]} for a in AREAS])}{_same_as_json},
    "aggregateRating": {_aggregate_rating},
    "review": {_reviews_json}
  }}
  </script>"""

# ─────────────────────────────────────────────────────────
# HELPER: Service card header (photo or emoji icon)
# ─────────────────────────────────────────────────────────

def service_card_header(s):
    if s.get("image"):
        img_src = s["image"]
        # Prepend BASE if path starts with /
        if img_src.startswith("/") and not img_src.startswith(BASE):
            img_src = BASE + img_src
        return f'<img class="service-card-img" src="{img_src}" alt="{s["name"]}" loading="lazy" />'
    return f'<div class="service-card-placeholder" aria-hidden="true"></div>'


# ─────────────────────────────────────────────────────────
# HELPER: Gallery section (Our Work)
# ─────────────────────────────────────────────────────────

def gallery_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""      <figure class="gallery-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <figcaption>{item['label']}</figcaption>
      </figure>""")
        else:
            items.append(f"""      <div class="gallery-item gallery-placeholder-slot">
        <span class="gallery-slot-icon">{item.get('icon','')}</span>
        <span class="gallery-slot-label">{item['label']}</span>
      </div>""")
    items_html = "\n".join(items)
    return f"""
<!-- OUR WORK -->
<section class="section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Work</span>
      <h2>Recent Projects on Long Island</h2>
      <p>See the quality of our work across Nassau &amp; Suffolk Counties - from custom landscapes and patios to full outdoor renovation projects.</p>
    </div>
    <div class="gallery-grid">
{items_html}
    </div>
    <div class="text-center mt-4">
      <a href="{BASE}/request-service" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# HELPER: Our Work / Recent Projects section
# ─────────────────────────────────────────────────────────

def work_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""<div class="work-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <div class="work-item-label">{item['label']}</div>
      </div>""")
        else:
            items.append(f"""<div class="work-item work-item-placeholder">
        <div class="work-item-label">{item['label']}</div>
      </div>""")
    items_html = "\n      ".join(items)
    return f"""
<section class="section our-work-section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Portfolio</span>
      <h2>Recent Projects</h2>
      <p>A sample of our construction and renovation work across Nassau and Suffolk Counties.</p>
    </div>
    <div class="work-grid">
      {items_html}
    </div>
    <div class="text-center mt-4">
      <a href="{BASE}/request-service" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# PAGE: Homepage
# ─────────────────────────────────────────────────────────

def make_homepage():
    slides = B.get('heroSlides', ['/images/hero-bg.jpg'])
    # Prepend BASE to slide paths that start with /
    slides = [BASE + s if s.startswith("/") and not s.startswith(BASE) else s for s in slides]
    slide_divs = "\n    ".join(
        (f'<div class="hero-slide active"><img src="{s}" alt="" fetchpriority="high" /></div>' if i == 0 else
         f'<div class="hero-slide"><img data-src="{s}" alt="" /></div>')
        for i, s in enumerate(slides)
    )
    dot_buttons = "\n    ".join(
        f'<button class="hero-dot{" active" if i == 0 else ""}" data-slide="{i}" aria-label="Go to slide {i+1}"></button>'
        for i in range(len(slides))
    )
    service_cards_list = []
    for s in SERVICES:
        service_cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3>{s['name']}</h3>
        <p>{s['description']}</p>
        <a href="{BASE}/services/{s['slug']}/" class="card-link" aria-label="Learn more about {s['name']}">Learn More →</a>
      </div>
    </div>""")
    service_cards = "\n".join(service_cards_list)

    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS[:5])

    content = f"""{head(
        f"{B['industry']} in {B.get('homeArea', B['city'])}, NY | {NAME} | {PHONE}",
        f"{NAME} provides professional {B['industryLower']} in {B.get('homeArea', B['city'])}, NY. Call {PHONE} for a free estimate!",
        "/",
        LOCAL_BIZ_SCHEMA,
        f'<link rel="preload" as="image" href="{slides[0]}" fetchpriority="high" />'
    )}
{nav()}

<!-- HERO -->
<section class="hero" id="hero-carousel">
  <div class="hero-slides">
    {slide_divs}
  </div>
  <div class="hero-overlay"></div>
  <div class="container">
    <div class="hero-content">
      <span class="hero-badge">Nassau &amp; Suffolk Counties · Long Island, NY</span>
      <h1>{B['tagline']}</h1>
      <p id="hero-p">{B.get('heroSubtext', '')}</p>
      <div class="hero-actions">
        <a href="{BASE}/request-service" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
      </div>
      <div class="hero-trust">
        <span>{ICON["star"]} 5-Star Rated</span>
        <span>{ICON["shield"]} Insured</span>
        <span>{ICON["pin"]} Long Island Based</span>
      </div>
    </div>
  </div>
  <div class="hero-slide-dots">
    {dot_buttons}
  </div>
</section>
<script>
(function() {{
  var slides = document.querySelectorAll('#hero-carousel .hero-slide');
  var dots   = document.querySelectorAll('#hero-carousel .hero-dot');
  var cur = 0, timer;
  function loadBg(el) {{
    if (el) {{ var img = el.querySelector('img'); if (img && img.dataset.src && !img.getAttribute('src')) {{ img.src = img.dataset.src; }} }}
  }}
  function goTo(n) {{
    slides[cur].classList.remove('active');
    dots[cur].classList.remove('active');
    cur = (n + slides.length) % slides.length;
    loadBg(slides[cur]);
    slides[cur].classList.add('active');
    dots[cur].classList.add('active');
  }}
  function next() {{ goTo(cur + 1); }}
  function start() {{ timer = setInterval(next, 5500); }}
  function stop()  {{ clearInterval(timer); }}
  dots.forEach(function(dot, i) {{
    dot.addEventListener('click', function() {{ stop(); goTo(i); start(); }});
  }});
  var hero = document.getElementById('hero-carousel');
  hero.addEventListener('mouseenter', stop);
  hero.addEventListener('mouseleave', start);
  start();
  window.addEventListener('load', function() {{ slides.forEach(loadBg); document.querySelector('#hero-carousel .hero-slides').classList.add('animated'); }});
}})();
</script>

<!-- STATS -->
<div class="stats-bar">
  <div class="container stats-grid">
    <div class="stat"><span class="stat-n">15+</span><span class="stat-l">Years Combined Experience</span></div>
    <div class="stat"><span class="stat-n">500+</span><span class="stat-l">Projects Delivered</span></div>
    <div class="stat"><span class="stat-n">{len(AREAS)}+</span><span class="stat-l">Long Island Communities</span></div>
    <div class="stat"><span class="stat-n">5★</span><span class="stat-l">Rated by Homeowners</span></div>
  </div>
</div>

<!-- CONTACT CARDS -->
<section class="contact-cards-section">
  <div class="container contact-cards-grid">
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.44 2 2 0 0 1 3.6 1.25h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.82a16 16 0 0 0 6.29 6.29l.94-.94a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      </div>
      <h2>Call Us</h2>
      <p>Speak directly with our team - quick response guaranteed</p>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">{PHONE}</a>
    </div>
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
      </div>
      <h2>Email Us</h2>
      <p>Send us your project details and we'll follow up promptly</p>
      <a href="mailto:{B['email']}" class="btn btn-outline-white">{B['email']}</a>
    </div>
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
      </div>
      <h2>Free Estimate</h2>
      <p>No pressure, no obligation - just honest pricing upfront</p>
      <a href="{BASE}/request-service" class="btn btn-secondary">Get Started</a>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section class="section section-light how-it-works">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Simple Process</span>
      <h2>How It Works</h2>
      <p>From first call to finished project - here's what to expect.</p>
    </div>
    <div class="process-grid">
      <div class="process-step">
        <div class="process-number">1</div>
        <h3>Tell Us Your Vision</h3>
        <p>Call or fill out our form. Describe the project - whether it's a single repair or a full renovation. We'll ask questions to understand the scope.</p>
      </div>
      <div class="process-step">
        <div class="process-number">2</div>
        <h3>We Assess & Quote</h3>
        <p>We visit your home, review the work needed, and provide a transparent estimate. No surprises, no hidden fees - just honest pricing.</p>
      </div>
      <div class="process-step">
        <div class="process-number">3</div>
        <h3>We Build It Right</h3>
        <p>Our crew handles every detail from start to finish. We keep you updated throughout and don't leave until the job meets your standards.</p>
      </div>
    </div>
    <div class="text-center" style="margin-top:2.5rem">
      <a href="{BASE}/request-service" class="btn btn-primary btn-lg">Start Your Project</a>
    </div>
  </div>
</section>

<!-- THE DIFFERENCE -->
<section class="difference-section">
  <div class="container">
    <div class="section-header section-header-light">
      <span class="eyebrow-light">Why Choose Us</span>
      <h2>The {NAME} Difference</h2>
    </div>
    <div class="difference-grid">
      <div class="difference-card">
        <div class="icon-circle icon-circle-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>
        </div>
        <h3>Insured</h3>
        <p>We carry liability insurance for your protection on every project we take on.</p>
      </div>
      <div class="difference-card">
        <div class="icon-circle icon-circle-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        </div>
        <h3>Custom Approach</h3>
        <p>Every project is designed around your vision, your property, and your budget - not a cookie-cutter template.</p>
      </div>
      <div class="difference-card">
        <div class="icon-circle icon-circle-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <h3>Responsive Service</h3>
        <p>We respond within 1 business hour and keep you informed throughout your project.</p>
      </div>
      <div class="difference-card">
        <div class="icon-circle icon-circle-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        </div>
        <h3>100% Satisfaction</h3>
        <p>The job isn't finished until it meets your standard. We back every project with a workmanship warranty.</p>
      </div>
    </div>
  </div>
</section>

<!-- SERVICES -->
<section class="section" id="services">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What We Do For You</span>
      <h2>{B.get('servicesHeadline', f'{B.get("industry","Professional")} Services for Long Island')}</h2>
      <p>{B.get('servicesSubtext', f'Professional {B.get("industryLower","services")} for Long Island homeowners and businesses.')}</p>
    </div>
    <div class="service-grid">
      {service_cards}
    </div>
  </div>
</section>

{work_section()}

<!-- BOOK A CONSULTATION -->
<section class="consultation-section">
  <div class="container consultation-content">
    <div class="consultation-text">
      <span class="eyebrow-light">Get Started</span>
      <h2>Book a Free Consultation</h2>
      <p>Ready to start your project? Schedule a free on-site consultation. We'll walk your property, listen to your goals, and give you a detailed quote - no pressure, no obligation.</p>
      <ul class="consult-list">
        <li>{ICON["check"]} Free on-site visit</li>
        <li>{ICON["check"]} Detailed written quote</li>
        <li>{ICON["check"]} Response within 1 hour</li>
        <li>{ICON["check"]} No commitment required</li>
      </ul>
    </div>
    <div class="consultation-form-wrap">
      {booking_form(compact=True)}
    </div>
  </div>
</section>

<!-- REVIEWS -->
<section class="section section-light" id="reviews">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Client Reviews</span>
      <h2>What Long Island Homeowners Say</h2>
      <div class="google-badge">{GOOGLE_G} <strong>5.0</strong> <span class="review-stars">{ICON["star"] * 5}</span> · Based on <a href="{GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener">32 Google reviews</a></div>
    </div>
    <div class="review-grid">
      {review_cards()}
    </div>
    <div class="text-center mt-4">
      <a href="{BASE}/reviews/" class="btn btn-outline">Read More Reviews</a>
    </div>
  </div>
</section>

<!-- SERVICE AREAS -->
<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Service Areas</span>
      <h2>Serving Nassau &amp; Suffolk Counties</h2>
      <p>We cover all of Long Island. Don't see your city? Call us - we likely serve you.</p>
    </div>
    <div class="city-grid">
      {service_area_links()}
    </div>
  </div>
</section>

<!-- FAQ PREVIEW -->
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">FAQ</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    <div class="faq-list">
      {faq_items}
    </div>
    <div class="text-center mt-4">
      <a href="{BASE}/faq/" class="btn btn-outline">See All FAQs</a>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Start Your Project?</h2>
    <p>No pressure, no obligation - just honest work and fair pricing from a team that knows Long Island.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get a Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service detail pages
# ─────────────────────────────────────────────────────────

def make_service_page(s):
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", "/services/"), (s["name"], None)])
    bullets = "\n".join(f"<li>{b}</li>" for b in s["bullets"])
    svc_img = s.get("image", "")
    # Prepend BASE if path starts with /
    if svc_img and svc_img.startswith("/") and not svc_img.startswith(BASE):
        svc_img = BASE + svc_img
    hero_class = "page-hero page-hero-photo" if svc_img else "page-hero"
    hero_style = f' style="background-image:url(\'{svc_img}\')"' if svc_img else ""
    other_services = "\n".join(
        f'<a href="{BASE}/services/{o["slug"]}/" class="related-link">{o["name"]}</a>'
        for o in SERVICES if o["slug"] != s["slug"]
    )

    # Service-specific FAQs
    service_faqs = s.get("faqs", [])
    faq_html = ""
    if service_faqs:
        faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in service_faqs)
        faq_html = f"""
<section class="section">
  <div class="container" style="max-width:800px">
    <h2 class="text-center mb-4">Frequently Asked Questions</h2>
    <div class="faq-list">{faq_items}</div>
  </div>
</section>
"""

    # Show only 8 priority locations, link to full list
    priority_areas = AREAS[:8]
    area_links = "\n".join(
        f'<a href="{BASE}/service-areas/{a["slug"]}/" class="city-pill">{a["name"]}</a>'
        for a in priority_areas
    )

    content = f"""{head(
        f"{s['name']} in Nassau & Suffolk Counties | {NAME} | {PHONE}",
        f"Professional {s['name'].lower()} across Nassau and Suffolk Counties. {NAME} - insured and locally based. Call {PHONE} for a free estimate.",
        f"/services/{s['slug']}/",
        bc_schema
    )}
{nav(active="services")}
{bc}

<section class="{hero_class}"{hero_style}>
  <div class="container">
    <h1>{s['name']}</h1>
    <p>{s['description']}</p>
    <div class="hero-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Professional {s['name']} on Long Island</h2>
      <p>{s['heroText']}</p>
      <h3>What's Included</h3>
      <ul class="check-list">{bullets}</ul>
      <h3>Why Choose {NAME}?</h3>
      <p>We're locally owned and operated - not a national franchise. Every job is handled by our trained crew, and we back every service with our workmanship warranty.</p>
      <div class="cta-inline">
        <a href="{BASE}/request-service" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline">Call {PHONE}</a>
      </div>
      <h3>Service Areas</h3>
      <p>We provide {s['name'].lower()} throughout Long Island including:</p>
      <div class="city-grid city-grid-sm">
        {area_links}
      </div>
      <p class="mt-2"><a href="{BASE}/service-areas/">View all service areas →</a></p>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>
{service_gallery(s['slug'], s['name'])}
{faq_html}
<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What Customers Say</h2>
    <div class="review-grid">{review_cards()}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="text-center mb-4">Other Services We Offer</h2>
    <div class="related-grid">{other_services}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need {s['name']} on Long Island?</h2>
    <p>Call or fill out the form above - we respond within 1 business hour with a free estimate.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"services/{s['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Services hub
# ─────────────────────────────────────────────────────────

def make_services_hub():
    cards_list = []
    for s in SERVICES:
        cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3><a href="{BASE}/services/{s['slug']}/">{s['name']}</a></h3>
        <p>{s['description']}</p>
        <a href="{BASE}/services/{s['slug']}/" class="card-link" aria-label="Learn more about {s['name']}">Learn More →</a>
      </div>
    </div>""")
    cards = "\n".join(cards_list)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", None)])
    content = f"""{head(
        f"{B['industry']} | {NAME} | {PHONE}",
        f"{NAME} offers professional {B['industryLower']} in {B['city']}, NY. Call {PHONE} for a free estimate.",
        "/services/",
        bc_schema
    )}
{nav(active="services")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Our {B['industry']} Services</h1>
    <p>Professional {B['industryLower']} for Long Island homeowners. Custom work, premium materials, and certified craftsmanship - locally based in {B['city']}, NY.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="service-grid">{cards}</div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Not Sure What You Need?</h2>
    <p>Call us and describe your property - we'll recommend the right services and give you a free estimate.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("services/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: City / Service Area pages
# ─────────────────────────────────────────────────────────

def make_city_page(area):
    city = area["name"]
    slug = area["slug"]
    county = area["county"]
    # Get nearby areas from config or generate from other areas in same county
    nearby_list = area.get("nearbyAreas", [a["name"] for a in AREAS if a["name"] != city and a.get("county") == county][:5])
    nearby = ", ".join(f"<strong>{n}</strong>" for n in nearby_list)
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", "/service-areas/"), (city, None)])

    city_schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME} - {city}","url":"https://{B['domain']}/service-areas/{slug}/",
    "telephone":"{PHONE}","priceRange":"$$",
    "address":{{"@type":"PostalAddress","addressLocality":"{city}","addressRegion":"{B['state']}","addressCountry":"US"}},
    "areaServed":{{"@type":"City","name":"{city}"}}
  }}
  </script>"""

    service_list = "\n".join(
        f'<li><a href="{BASE}/services/{s["slug"]}/">{s["name"]} in {city}</a></li>'
        for s in SERVICES
    )

    content = f"""{head(
        f"{B['industry']} in {city}, NY | {NAME} | {PHONE}",
        f"Professional {B['industryLower']} in {city}, NY. {NAME} serves {city} and {county} County. Call {PHONE} for a free estimate.",
        f"/service-areas/{slug}/",
        bc_schema + city_schema
    )}
{nav(active="areas")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>{B['industry']} in {city}, NY</h1>
    <p>{NAME} serves {city} and surrounding {county} County homeowners. Call {PHONE} for a free estimate today.</p>
    <div class="hero-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Your Local {B['industry']} Experts in {city}</h2>
      <p>When {city} homeowners need reliable {B['industryLower']}, they call {NAME}. We're a locally owned company based in {B['city']}, serving {county} County with the personal attention that national franchises can't match. Our team knows Long Island properties and delivers consistent, high-quality work on every project.</p>
      <p>From kitchen remodels and bathroom renovations to home repairs, carpentry, and room updates, we help {city} homeowners take care of the projects that have been waiting to get done.</p>

      <h3>Services We Offer in {city}, NY</h3>
      <ul class="check-list">{service_list}</ul>

      <h3>Areas Near {city} We Also Serve</h3>
      <p>In addition to {city}, we serve {nearby} and more throughout {county} County.
      <a href="{BASE}/service-areas/">View all service areas →</a></p>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What {city} Residents Say</h2>
    <div class="review-grid">{review_cards(city)}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need {B['industry']} in {city}, NY?</h2>
    <p>We're nearby and ready. Call or submit the form - response within 1 business hour.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"service-areas/{slug}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service Areas hub
# ─────────────────────────────────────────────────────────

def make_areas_hub():
    nassau = [a for a in AREAS if a["county"] == "Nassau"]
    suffolk = [a for a in AREAS if a["county"] == "Suffolk"]
    def area_cards(areas):
        return "\n".join(f"""
        <a href="{BASE}/service-areas/{a['slug']}/" class="area-card">
          <h3>{a['name']}</h3>
          <span>{a['county']} County</span>
        </a>""" for a in areas)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", None)])
    content = f"""{head(
        f"{B['industry']} Service Areas - Long Island, NY | {NAME}",
        f"{NAME} serves Nassau and Suffolk Counties on Long Island. Click your city to see local {B['industryLower']} services and get a free estimate.",
        "/service-areas/",
        bc_schema
    )}
{nav(active="areas")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Long Island {B['industry']} Service Areas</h1>
    <p>{NAME} covers Nassau and Suffolk Counties. Select your city for local {B['industryLower']} information and a free estimate.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2>Nassau County</h2>
    <div class="area-grid">{area_cards(nassau)}</div>
    <h2 class="mt-4">Suffolk County</h2>
    <div class="area-grid">{area_cards(suffolk)}</div>
    <p class="mt-4" style="color:var(--text-mid)">Don't see your city? <a href="tel:{PHONE_RAW}">Call us at {PHONE}</a> - we likely serve your area.</p>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Serving All of Long Island</h2>
    <p>Call or request online for service in your area.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("service-areas/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: About
# ─────────────────────────────────────────────────────────

def make_about():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("About Us", None)])
    content = f"""{head(
        f"About Us | {NAME} - Nassau & Suffolk Counties",
        f"Learn about {NAME}, Long Island's trusted {B['industryLower']} company. Locally owned and insured, serving Nassau and Suffolk Counties.",
        "/about/",
        bc_schema
    )}
{nav(active="about")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>About {NAME}</h1>
    <p>Home repairs, room updates, and remodeling across Nassau and Suffolk Counties.</p>
  </div>
</section>

<section class="section">
  <div class="container about-content">
    <div class="about-intro">
      <h2>For the Projects That Have Been Waiting to Get Done</h2>
      <p>Sometimes a home needs more than one repair. The ceiling needs patching and painting. A door and its frame need replacing. The trim needs attention, and the flooring is ready for an update. Other times, it's a kitchen or bathroom that no longer works the way you want it to.</p>
      <p>{NAME} helps Long Island homeowners bring those projects together.</p>
      <p>GOAT is a locally owned, insured handyman and home improvement company serving Nassau and Suffolk Counties. Our focus is on practical repairs and remodeling that improve how your home looks, functions, and feels.</p>
    </div>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="split-section split-section-reverse">
      <div class="split-img"><img src="{BASE}/images/about-team.png" alt="{NAME} team - locally owned and operated" loading="lazy" width="600" height="450" class="about-photo" /></div>
      <div class="split-content">
        <span class="eyebrow">Our Approach</span>
        <h2>A Handyman Company That Can Take On the Bigger Picture</h2>
        <p>Many homeowners hear "handyman" and think of a single small task. Our work also includes projects that require several types of repair, installation, and finishing.</p>
        <p>That might mean repairing a water-damaged ceiling after the leak has been resolved, then preparing and painting the surface. It could involve replacing doors, repairing the surrounding drywall, and installing new trim. Or it might be updating several rooms as part of one home improvement project.</p>
        <p>These connected projects are an important part of what GOAT does. We help homeowners think through the full scope, including the finishing work that can be easy to overlook at the beginning.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What We Do</span>
      <h2>The Work We Handle</h2>
      <p>Our services cover interior and exterior home improvements.</p>
    </div>
    <div class="services-summary-grid">
      <div class="service-summary-card">
        <h3>Home Repairs &amp; Interior Finishing</h3>
        <p>Handyman services, drywall repair and installation, painting, carpentry, trim, and molding.</p>
      </div>
      <div class="service-summary-card">
        <h3>Doors, Windows &amp; Flooring</h3>
        <p>Repair and installation, including the surrounding finish work identified in the project scope.</p>
      </div>
      <div class="service-summary-card">
        <h3>Kitchen &amp; Bathroom Remodeling</h3>
        <p>Updates, repairs, and renovations based on the existing space and your goals.</p>
      </div>
      <div class="service-summary-card">
        <h3>Exterior Improvements</h3>
        <p>Deck repairs and installation, along with siding repairs and replacement (vinyl, wood, fiber cement, aluminum).</p>
      </div>
      <div class="service-summary-card">
        <h3>Insulation</h3>
        <p>Attic, wall, crawl-space, and basement insulation, including removal and replacement (fiberglass and spray foam).</p>
      </div>
    </div>
    <p class="text-center mt-4"><a href="{BASE}/services/" class="btn btn-outline">View All Services</a></p>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Process</span>
      <h2>How We Approach Your Project</h2>
    </div>
    <div class="about-process">
      <p>We start with what you want to accomplish: fixing damage, updating a room, replacing worn materials, or taking care of several overdue repairs.</p>
      <p>From there, the important questions are practical. What can be repaired? What needs replacement? Which materials will work with what is already there? What preparation and finishing should be included?</p>
      <p>Our aim is to make those decisions clear before work begins. We want the project scope to account for the details—from drywall preparation and trim to caulking and paint—so the finished work makes sense as a whole.</p>
      <p><strong>GOAT provides a workmanship warranty on completed work.</strong></p>
    </div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Let's Talk About Your Home</h2>
    <p>Whether you have a list of repairs or a room you're ready to improve, tell us what you have in mind.</p>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Request an Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("about/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: FAQ
# ─────────────────────────────────────────────────────────

def make_faq():
    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS)

    faq_schema_items = json.dumps([{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in FAQS])
    faq_schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_schema_items}}}</script>'

    bc, bc_schema = breadcrumbs([("Home", "/"), ("FAQ", None)])
    content = f"""{head(
        f"FAQ - {B['industry']} Questions Answered | {NAME}",
        f"Common questions about {NAME}'s {B['industryLower']} services on Long Island. Get answers about cost, estimates, timelines, and more.",
        "/faq/",
        bc_schema + faq_schema
    )}
{nav(active="faq")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Frequently Asked Questions</h1>
    <p>Everything you need to know about {NAME}'s services on Long Island.</p>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width:800px">
    <div class="faq-list">{faq_items}</div>
    <div class="cta-inline mt-4">
      <p>Still have questions? <a href="tel:{PHONE_RAW}">Call or text us at {PHONE}</a> - we respond within 1 business hour.</p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Get Started?</h2>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("faq/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Reviews
# ─────────────────────────────────────────────────────────

def make_reviews():
    all_reviews = review_cards()

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Reviews", None)])
    content = f"""{head(
        f"Customer Reviews | {NAME} - Long Island, NY",
        f"Read reviews from satisfied customers of {NAME} in {B['city']}, NY and Long Island. See why we're rated 5 stars.",
        "/reviews/",
        bc_schema
    )}
{nav(active="reviews")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Customer Reviews</h1>
    <p>See what Long Island homeowners and businesses say about {NAME}.</p>
    <div class="google-badge">{GOOGLE_G} <strong>5.0</strong> <span class="review-stars">{ICON["star"] * 5}</span> · Based on <a href="{GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener">32 Google reviews</a></div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="review-grid">{all_reviews}</div>
    <div class="cta-inline mt-4 text-center">
      <p>Want to leave a review? <a href="https://g.page/r/CTg78e2A46fiEAI/review" target="_blank" rel="noopener">Leave us a Google review →</a></p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Join Our Happy Customers</h2>
    <div class="cta-actions">
      <a href="{BASE}/request-service" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("reviews/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Request Service
# ─────────────────────────────────────────────────────────

def make_request_service():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Request Service", None)])
    content = f"""{head(
        f"Request a Free Estimate | {NAME} | {PHONE}",
        f"Request a free {B['industryLower']} estimate from {NAME} in {B['city']}, NY. We serve all of Long Island and respond within 1 business hour.",
        "/request-service",
        bc_schema
    )}
{nav()}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Request a Free Estimate</h1>
    <p>Fill out the form and we'll get back to you within 1 business hour. No pressure, no obligation.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="content-sidebar-layout">
      <div class="content-main">
        <h2>Let's Talk About Your Project</h2>
        <p>Whether it is a single room remodel or a full home addition, we are here to help. Tell us about your project and we will provide a free, transparent estimate.</p>
        <div class="features-grid" style="margin-top:2rem">
          <div class="feature-card">{ICON["phone_lg"]}<h3>Call or Text</h3><p><a href="tel:{PHONE_RAW}">{PHONE}</a><br/>Sun-Fri, 8am-6pm ET</p></div>
          <div class="feature-card">{ICON["pin_lg"]}<h3>Our Location</h3><p>{ADDRESS}</p></div>
          <div class="feature-card">{ICON["timer_lg"]}<h3>Response Time</h3><p>Within 1 business hour</p></div>
        </div>
        <div style="margin-top:2rem;border-radius:8px;overflow:hidden">
          <iframe src="{B['googleMapsEmbed']}" width="100%" height="300" style="border:0;display:block" allowfullscreen loading="lazy" title="{NAME} Location Map"></iframe>
        </div>
      </div>
      <aside class="content-sidebar">
        {booking_form()}
      </aside>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("request-service.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Thank You
# ─────────────────────────────────────────────────────────

def make_thank_you():
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  {GA4_TAG}
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Request Received | {NAME}</title>
  <meta name="robots" content="noindex" />
  <link rel="icon" href="/images/logo.png" type="image/png" />
  <link rel="apple-touch-icon" href="/images/logo.png" />
  <link rel="preload" as="font" type="font/woff2" href="/fonts/inter-latin.woff2" crossorigin />
  <link rel="preload" as="font" type="font/woff2" href="/fonts/outfit-latin.woff2" crossorigin />
  <style>{FONTS_FACE}</style>
  <link rel="stylesheet" href="/css/main.css" />
  <link rel="stylesheet" href="/css/theme.css" />
  <link rel="stylesheet" href="{BASE}/css/builders-design.css" />
</head>
<body>
<header class="site-header">
  <nav class="main-nav"><div class="container nav-inner">
    <a href="{BASE}/" class="nav-logo"><img src="{BASE}/images/logo.png" alt="{NAME}" width="42" height="48" /></a>
    <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
  </div></nav>
</header>

<section class="ty-hero">
  <div class="container ty-hero-inner">
    <div class="ty-check">
      <svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" width="64" height="64">
        <circle cx="26" cy="26" r="26" fill="var(--green-light)"/>
        <path d="M15 27l8 8 14-16" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1>Your Request Was Received</h1>
    <p>Thanks for contacting {NAME}. A member of our team will reach out to you within <strong>1 business hour</strong>.</p>
    <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-lg">Call Us Now - {PHONE}</a>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What Happens Next</span>
      <h2>Here's What to Expect</h2>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">We'll Be in Touch</h3>
        <p class="step-desc">Expect a call or text from our team within 1 business hour. We'll confirm your request and answer any questions you have right away.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">Free On-Site Consultation</h3>
        <p class="step-desc">We'll visit your property, walk the space with you, and listen to your vision. No pressure - just an honest conversation about what's possible.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">Your Custom Quote</h3>
        <p class="step-desc">You'll receive a detailed, transparent quote before any work begins. No surprises, no hidden fees - just clear pricing for exactly what you asked for.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="text-align:center;max-width:560px;margin:0 auto">
    <h2>While You Wait</h2>
    <p style="color:var(--gray-mid);margin-bottom:2rem">Browse our services to get inspired, or read what Long Island homeowners are saying about us.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="{BASE}/services/" class="btn btn-outline">Browse Services</a>
      <a href="{BASE}/reviews/" class="btn btn-outline">Read Reviews</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("thank-you.html", content)


# ─────────────────────────────────────────────────────────
# PAGES: Blog articles
# ─────────────────────────────────────────────────────────

def make_blog_pages():
    posts = [
        {
            "slug": "landscaping-zones",
            "title": "What Landscaping Zone Are You in - and Why Does It Matter?",
            "desc": "Learn about USDA hardiness zones and how to choose plants that thrive on Long Island.",
            "body": f"""
<p>If your plants keep dying or struggling through Long Island winters, hardiness zones might be the answer. Long Island falls primarily in <strong>USDA Zone 7a-7b</strong> - which means cold winters (as low as 0-10°F) and warm, humid summers. Knowing your zone changes what you plant and when you plant it.</p>
<h2>What Zone Is Long Island?</h2>
<p>Most of Nassau and Suffolk Counties fall in Zone 7a or 7b. The North Shore tends to be slightly cooler; the South Shore and coastal areas are a bit warmer. This matters for anything you're keeping year-round - trees, shrubs, perennials, and ornamental grasses all have zone requirements.</p>
<h2>Best Plants for Long Island Landscapes</h2>
<ul>
  <li><strong>Ornamental grasses</strong> - drought-tolerant and low-maintenance in Zone 7</li>
  <li><strong>Knockout roses</strong> - disease-resistant and reliable in this climate</li>
  <li><strong>Boxwood</strong> - classic hedge material that handles Long Island winters well</li>
  <li><strong>Japanese maples</strong> - thrive in Zone 7, stunning fall color</li>
  <li><strong>Blue Star juniper</strong> - evergreen, low-maintenance, great for borders</li>
</ul>
<h2>What Our Team Recommends</h2>
<p>At {NAME}, every landscape design starts with a site visit where we assess your soil, sun exposure, drainage, and existing plantings. We only recommend plants we know will thrive on Long Island - not whatever looks good at a nursery in the moment.</p>
<p>Want a plant selection that will actually last? <a href="{BASE}/request-service">Request a free consultation</a> and we'll walk your property and give you honest recommendations.</p>"""
        },
        {
            "slug": "outdoor-landscaping-ideas",
            "title": "Outdoor Landscaping Ideas for Every Budget",
            "desc": "Creative outdoor renovation ideas for Long Island homeowners - from patio builds to full landscape transformations.",
            "body": f"""
<p>You don't need to spend a fortune to dramatically improve your outdoor space. Here are ideas across every budget range - from simple weekend projects to full outdoor renovations.</p>
<h2>Under $2,000 - Quick Impact</h2>
<ul>
  <li><strong>Define your garden beds</strong> - fresh mulch and clean edge lines transform the look of any yard instantly</li>
  <li><strong>Add a focal point</strong> - a single ornamental tree, a decorative boulder, or a simple planting cluster draws the eye and anchors the space</li>
  <li><strong>Upgrade your walkway edging</strong> - simple steel or stone edging along a path adds structure without major cost</li>
</ul>
<h2>$2,000-$10,000 - Real Transformation</h2>
<ul>
  <li><strong>Paver patio</strong> - a modest 200-300 sq ft patio adds usable outdoor living space and significant property value</li>
  <li><strong>Front yard redesign</strong> - new plantings, bed design, and lawn restoration can completely change your curb appeal</li>
  <li><strong>Privacy plantings</strong> - a row of arborvitae or holly creates a natural privacy screen that improves with age</li>
</ul>
<h2>$10,000+ - Full Outdoor Renovation</h2>
<ul>
  <li><strong>Complete back yard overhaul</strong> - patio, garden beds, lawn restoration, and plantings as a cohesive design</li>
  <li><strong>Outdoor living environment</strong> - pergola, fire feature, outdoor kitchen, and entertaining space</li>
  <li><strong>Paver driveway</strong> - one of the highest ROI upgrades for Long Island homes</li>
</ul>
<p>Not sure what fits your budget and property? {NAME} offers free on-site consultations where we can help you prioritize and plan. <a href="{BASE}/request-service">Book yours today.</a></p>"""
        },
        {
            "slug": "spring-lawn-tuneup",
            "title": "Why You Should Schedule a Spring Tune-Up for Your Landscape",
            "desc": "Spring is the best time to set your Long Island landscape up for the season. Here's what a professional spring tune-up includes and why it matters.",
            "body": f"""
<p>Winter on Long Island is tough on landscapes. Frost heaving, salt spray from roads, compacted soil, and dormant damage all add up. A professional spring tune-up addresses all of it before the growing season starts - and the difference shows all year.</p>
<h2>What a Spring Landscape Tune-Up Includes</h2>
<ul>
  <li><strong>Cleanup</strong> - removal of winter debris, dead material, and fallen branches</li>
  <li><strong>Bed edging and reshaping</strong> - clean lines define the space and prepare beds for new growth</li>
  <li><strong>Mulch application</strong> - fresh mulch retains moisture, suppresses weeds, and gives beds a finished look</li>
  <li><strong>Pruning</strong> - late-winter pruning of ornamentals and shrubs promotes healthy growth and shape</li>
  <li><strong>Lawn assessment</strong> - identify bare or damaged spots early and address them before summer heat sets in</li>
</ul>
<h2>Why Timing Matters</h2>
<p>The window for effective spring prep on Long Island is roughly <strong>late March through early May</strong>. Too early and the ground is still frozen; too late and fast-growing weeds get ahead of you. Getting on the schedule early means your property looks great from the first warm weekend.</p>
<h2>Book Before the Rush</h2>
<p>Spring is our busiest season. If you want to get on the schedule, reach out in late winter - spots fill up fast. <a href="{BASE}/request-service">Request a free estimate</a> and we'll assess your property and put together a spring plan.</p>"""
        }
    ]
    for post in posts:
        bc, bc_schema = breadcrumbs([("Home", "/"), ("Resources", None), (post["title"][:40] + "…", None)])
        content = f"""{head(
            f"{post['title']} | {NAME}",
            post["desc"],
            f"/blog/{post['slug']}/",
            bc_schema
        )}
{nav()}{bc}
<section class="page-hero">
  <div class="container">
    <h1>{post['title']}</h1>
  </div>
</section>
<section class="section">
  <div class="container blog-post-layout">
    <article class="blog-post-body">
      {post['body']}
      <div class="blog-post-cta">
        <h3>Ready to Transform Your Outdoor Space?</h3>
        <p>{NAME} serves all of Long Island - Nassau &amp; Suffolk Counties. Free estimates, no obligation.</p>
        <a href="{BASE}/request-service" class="btn btn-primary">Get a Free Estimate</a>
      </div>
    </article>
    <aside class="blog-post-sidebar">
      <div class="booking-card">
        <div class="booking-card-header">
          <h3>Free Estimate</h3>
          <p>Response within 1 business hour</p>
        </div>
        <div style="padding:20px">
          <p style="font-size:.9rem;color:var(--gray-dark);margin-bottom:16px">Ready to get started? Call or text us and we'll schedule a free on-site consultation.</p>
          <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-block">Call {PHONE}</a>
          <a href="{BASE}/request-service" class="btn btn-outline btn-block" style="margin-top:10px">Request Online</a>
        </div>
      </div>
      <div class="sidebar-services">
        <h4>Our Services</h4>
        <ul>{"".join(f'<li><a href="{BASE}/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)}</ul>
      </div>
    </aside>
  </div>
</section>
{footer()}
</body></html>"""
        write(f"blog/{post['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Privacy Policy & Terms (boilerplate)
# ─────────────────────────────────────────────────────────

def make_legal():
    for slug, title, body in [
        ("privacy-policy", "Privacy Policy", f"<p>{NAME} respects your privacy. We collect contact information submitted through our forms solely to respond to your service inquiry. We do not sell or share your information with third parties. For questions, call {PHONE}.</p>"),
        ("terms", "Terms of Use", f"<p>By using this website, you agree to these terms of use. All content on this site is owned by {NAME}. Unauthorized reproduction is prohibited. For questions, contact us at {PHONE}.</p>"),
        ("accessibility", "Accessibility", f"<p>{NAME} is committed to ensuring this website is accessible to people with disabilities. If you experience any difficulty, please call us at {PHONE} and we will assist you.</p>"),
    ]:
        bc, bc_schema = breadcrumbs([("Home", "/"), (title, None)])
        content = f"""{head(f"{title} | {NAME}", f"{title} for {NAME}, {B['city']}, NY.", f"/{slug}", bc_schema)}
{nav()}{bc}
<section class="page-hero"><div class="container"><h1>{title}</h1></div></section>
<section class="section"><div class="container" style="max-width:800px">{body}</div></section>
{footer()}</body></html>"""
        write(f"{slug}.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Sitemap + Robots
# ─────────────────────────────────────────────────────────

def make_sitemap():
    from datetime import date
    today = date.today().isoformat()
    urls = [("/", "1.0", "weekly")]
    urls += [(f"/services/{s['slug']}/", "0.9", "monthly") for s in SERVICES]
    urls += [("/services/", "0.8", "monthly")]
    urls += [(f"/service-areas/{a['slug']}/", "0.8", "monthly") for a in AREAS]
    urls += [("/service-areas/", "0.7", "monthly")]
    urls += [("/about/", "0.6", "monthly"), ("/faq/", "0.7", "monthly"),
             ("/reviews/", "0.6", "monthly"), ("/request-service", "0.8", "monthly")]
    items = "\n".join(f"""  <url>
    <loc>https://{B['domain']}{u}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""" for u, pri, freq in urls)
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>""")

def make_robots():
    write("robots.txt", f"""User-agent: *
Allow: /
Disallow: /thank-you

Sitemap: https://{B['domain']}/sitemap.xml
""")


# ─────────────────────────────────────────────────────────
# RUN ALL GENERATORS
# ─────────────────────────────────────────────────────────

print(f"Generating {NAME} site...\n")

make_theme_css()
make_homepage()
make_services_hub()
for s in SERVICES:
    make_service_page(s)
make_areas_hub()
for a in AREAS:
    make_city_page(a)
make_about()
make_faq()
make_reviews()
make_request_service()
make_thank_you()
make_legal()
make_sitemap()
make_robots()

print(f"[OK] {len(pages_created)} pages generated:\n")
for p in sorted(pages_created):
    print(f"   {p}")

if pages_failed:
    print(f"\n[FAIL] {len(pages_failed)} failed:")
    for p in pages_failed:
        print(f"   {p}")

print(f"\nTotal: {len(pages_created)} pages")

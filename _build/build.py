# -*- coding: utf-8 -*-
"""
Generator για το site του Elite Physiotherapy by Tatiana Gkouwir.

    python _build/build.py

Παραγει: index.html, epikoinonia.html, τις ενοτητες, sitemap.xml, robots.txt.
Ολο το περιεχομενο ζει στο _build/structure.py.
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from structure import (  # noqa: E402
    SITE, CONTACT, TBD, SECTIONS, HOME_SERVICES, HOME_STATS, HOME_CREDS,
    HOME_STEPS, STRIP_WORDS, HOME_META,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,"
         "wght@0,400;0,500;0,600;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap")


# ---------------------------------------------------------------------------
# Βοηθητικα
# ---------------------------------------------------------------------------

def up(depth):
    """Σχετικο prefix προς τη ριζα."""
    return "../" * depth


def strip_tags(text):
    out, skip = [], False
    for ch in text:
        if ch == "<":
            skip = True
        elif ch == ">":
            skip = False
        elif not skip:
            out.append(ch)
    return "".join(out)


def meta_text(text):
    """Καθαρο κειμενο για meta description / JSON."""
    return (strip_tags(text)
            .replace("&amp;", "&").replace("&nbsp;", " ")
            .replace("&quot;", '"').replace("  ", " ").strip())


def esc_attr(text):
    return meta_text(text).replace("&", "&amp;").replace('"', "&quot;")


# --- CTA: αν δεν υπαρχει τηλεφωνο, ολα τα CTA δειχνουν στην επικοινωνια ---

def cta_primary(depth):
    if CONTACT["phone"]:
        return ('<a href="tel:%s" class="btn btn-primary">Καλέστε %s</a>'
                % (CONTACT["phone"], CONTACT["phone_label"]))
    return ('<a href="%sepikoinonia.html" class="btn btn-primary">Αίτημα ραντεβού</a>'
            % up(depth))


def cta_primary_block(depth):
    if CONTACT["phone"]:
        return ('<a href="tel:%s" class="btn btn-primary btn-block">%s</a>'
                % (CONTACT["phone"], CONTACT["phone_label"]))
    return ('<a href="%sepikoinonia.html" class="btn btn-primary btn-block">Αίτημα ραντεβού</a>'
            % up(depth))


def nav_cta(depth):
    if CONTACT["phone"]:
        return '<a href="tel:%s" class="btn btn-nav">Ραντεβού</a>' % CONTACT["phone"]
    return '<a href="%sepikoinonia.html" class="btn btn-nav">Ραντεβού</a>' % up(depth)


# ---------------------------------------------------------------------------
# JSON-LD
# ---------------------------------------------------------------------------

def business_schema():
    data = {
        "@context": "https://schema.org",
        "@type": ["Physiotherapy", "MedicalBusiness"],
        "@id": SITE["url"] + "/#clinic",
        "name": meta_text(SITE["name"]),
        "alternateName": SITE["short"],
        "description": meta_text(HOME_META["description"]),
        "url": SITE["url"] + "/",
        "image": SITE["url"] + "/" + SITE["logo"],
        "logo": SITE["url"] + "/" + SITE["logo"],
        "medicalSpecialty": "Physiotherapy",
        "availableService": [],
        "employee": {
            "@type": "Person",
            "name": meta_text(SITE["person"]),
            "jobTitle": SITE["role"],
            "alumniOf": {
                "@type": "CollegeOrUniversity",
                "name": "Αλεξάνδρειο Τεχνολογικό Εκπαιδευτικό Ίδρυμα Θεσσαλονίκης",
            },
            "memberOf": {
                "@type": "Organization",
                "name": "Πανελλήνιος Σύλλογος Φυσικοθεραπευτών",
            },
        },
    }
    for section in SECTIONS:
        if section["slug"] != "ypiresies":
            continue
        for page in section["pages"]:
            data["availableService"].append({
                "@type": "MedicalTherapy",
                "name": meta_text(page["title"]),
                "url": "%s/%s/%s.html" % (SITE["url"], section["slug"], page["slug"]),
            })
    if CONTACT["phone"]:
        data["telephone"] = CONTACT["phone"]
    if CONTACT["email"]:
        data["email"] = CONTACT["email"]
    if CONTACT["street"]:
        addr = {"@type": "PostalAddress", "streetAddress": CONTACT["street"],
                "addressCountry": "GR"}
        if CONTACT["locality"]:
            addr["addressLocality"] = CONTACT["locality"]
        if CONTACT["postal"]:
            addr["postalCode"] = CONTACT["postal"]
        data["address"] = addr
    if CONTACT["social"]:
        data["sameAs"] = [u for _, u in CONTACT["social"]]
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def breadcrumb_schema(trail):
    items = []
    for i, (name, href) in enumerate(trail, start=1):
        items.append({"@type": "ListItem", "position": i,
                      "name": meta_text(name), "item": href})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": items},
                      ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Head / Nav / Footer
# ---------------------------------------------------------------------------

def head(title, description, canonical, depth, extra_ld=None, keywords=None):
    r = up(depth)
    parts = [
        '<!DOCTYPE html>', '<html lang="el">', '<head>',
        '  <meta charset="UTF-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        '  <title>%s</title>' % title,
        '  <meta name="description" content="%s" />' % esc_attr(description),
    ]
    if keywords:
        parts.append('  <meta name="keywords" content="%s" />' % esc_attr(keywords))
    parts += [
        '  <meta name="author" content="%s" />' % esc_attr(SITE["name"]),
        '  <meta name="robots" content="index, follow, max-image-preview:large" />',
        '  <meta name="theme-color" content="#1e3a5f" />',
        '  <link rel="canonical" href="%s" />' % canonical,
        '',
        '  <meta property="og:site_name" content="%s" />' % esc_attr(SITE["name"]),
        '  <meta property="og:locale" content="el_GR" />',
        '  <meta property="og:type" content="website" />',
        '  <meta property="og:title" content="%s" />' % esc_attr(title),
        '  <meta property="og:description" content="%s" />' % esc_attr(description),
        '  <meta property="og:url" content="%s" />' % canonical,
        '  <meta property="og:image" content="%s/%s" />' % (SITE["url"], SITE["logo"]),
        '  <meta name="twitter:card" content="summary_large_image" />',
        '',
        '  <link rel="icon" type="image/jpeg" href="%s%s" />' % (r, SITE["logo"]),
        '  <link rel="apple-touch-icon" href="%s%s" />' % (r, SITE["logo"]),
        '  <link rel="preconnect" href="https://fonts.googleapis.com" />',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
        '  <link href="%s" rel="stylesheet" />' % FONTS,
        '  <link rel="stylesheet" href="%sstyles.css" />' % r,
        '  <script type="application/ld+json">%s</script>' % business_schema(),
    ]
    if extra_ld:
        parts.append('  <script type="application/ld+json">%s</script>' % extra_ld)
    parts += ['</head>', '<body>']
    return "\n".join(parts)


def nav(depth, current_section=None, current_page=None, home=False):
    r = up(depth)
    out = [
        '  <a class="skip-link" href="#main">Μετάβαση στο περιεχόμενο</a>',
        '  <header class="site-header" id="top">',
        '    <nav class="nav container" aria-label="Κύρια πλοήγηση">',
        '      <a href="%sindex.html" class="brand" aria-label="%s — Αρχική">'
        % (r, esc_attr(SITE["name"])),
        '        <img src="%s%s" alt="" class="brand-mark" width="267" height="636" />'
        % (r, SITE["mark"]),
        '        <span class="brand-text"><strong>Elite Physiotherapy</strong>'
        '<span>Κέντρο Φυσικοθεραπείας &amp; Αποκατάστασης</span></span>',
        '      </a>',
        '      <button class="nav-toggle" aria-label="Άνοιγμα μενού" aria-expanded="false">'
        '<span></span><span></span><span></span></button>',
        '      <ul class="nav-links">',
    ]
    aria = ' aria-current="page"' if home else ''
    out.append('        <li><a href="%sindex.html"%s>Αρχική</a></li>' % (r, aria))

    for section in SECTIONS:
        base = "" if depth and current_section == section["slug"] else "%s%s/" % (r, section["slug"])
        cur = ' aria-current="true"' if current_section == section["slug"] else ''
        sub = ['<li><a class="sub-head" href="%sindex.html">Όλα · %s</a></li>'
               % (base, section["title"])]
        for page in section["pages"]:
            pcur = ' aria-current="page"' if (current_section == section["slug"]
                                              and current_page == page["slug"]) else ''
            sub.append('<li><a href="%s%s.html"%s>%s</a></li>'
                       % (base, page["slug"], pcur, page["title"]))
        out.append('        <li class="has-sub"><a href="%sindex.html"%s>%s</a>'
                   '<ul class="sub">%s</ul></li>'
                   % (base, cur, section["title"], "".join(sub)))

    cur = ' aria-current="page"' if current_section == "epikoinonia" else ''
    out += [
        '        <li><a href="%sepikoinonia.html"%s>Επικοινωνία</a></li>' % (r, cur),
        '        <li>%s</li>' % nav_cta(depth),
        '      </ul>',
        '    </nav>',
        '  </header>',
    ]
    return "\n".join(out)


def cta_band(depth):
    r = up(depth)
    if CONTACT["locality"]:
        sub = "Το κέντρο δέχεται κατόπιν ραντεβού — %s." % CONTACT["locality"]
    else:
        sub = "Το κέντρο δέχεται κατόπιν ραντεβού."
    return "\n".join([
        '  <section class="cta-band">',
        '    <div class="container cta-inner">',
        '      <div>',
        '        <p class="eyebrow">Κλείστε το ραντεβού σας</p>',
        '        <h2 class="cta-title">Κάθε αποκατάσταση ξεκινά<br />από μια σωστή αξιολόγηση.</h2>',
        '        <p class="cta-sub">%s</p>' % sub,
        '      </div>',
        '      <div class="cta-actions">',
        '        %s' % cta_primary(depth),
        '        <a href="%sepikoinonia.html" class="btn btn-ghost">Στοιχεία Επικοινωνίας</a>' % r,
        '      </div>',
        '    </div>',
        '  </section>',
    ])


def footer(depth):
    r = up(depth)
    sec = {s["slug"]: s for s in SECTIONS}

    contact_lines = []
    if CONTACT["street"]:
        loc = CONTACT["locality"] or ""
        pc = ("Τ.Κ. " + CONTACT["postal"]) if CONTACT["postal"] else ""
        contact_lines.append("%s<br />%s %s" % (CONTACT["street"], loc, pc))
    else:
        contact_lines.append("Διεύθυνση: %s" % TBD)

    links = []
    if CONTACT["phone"]:
        links.append('<a href="tel:%s">Τηλ. %s</a>' % (CONTACT["phone"], CONTACT["phone_label"]))
    if CONTACT["mobile"]:
        links.append('<a href="tel:%s">Κιν. %s</a>' % (CONTACT["mobile"], CONTACT["mobile_label"]))
    if CONTACT["email"]:
        links.append('<a href="mailto:%s">%s</a>' % (CONTACT["email"], CONTACT["email"]))
    if not links:
        links.append('<a href="%sepikoinonia.html">Στοιχεία επικοινωνίας — %s</a>' % (r, TBD))

    social = "".join('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (u, n)
                     for n, u in CONTACT["social"])

    ypir = "".join('<a href="%sypiresies/%s.html">%s</a>' % (r, p["slug"], p["title"])
                   for p in sec["ypiresies"]["pages"])
    ther = "".join('<a href="%stherapeies/%s.html">%s</a>' % (r, p["slug"], p["title"])
                   for p in sec["therapeies"]["pages"])

    return "\n".join([
        '  <footer class="site-footer">',
        '    <div class="footer-inner">',
        '      <div class="footer-brand">',
        '        <img src="%s%s" alt="%s" class="footer-logo" width="1074" height="938" loading="lazy" />'
        % (r, SITE["logo"], esc_attr(SITE["short"])),
        '        <p class="footer-tag">Αξιολόγηση, θεραπεία, επανένταξη.</p>',
        '        <p class="footer-addr">%s<br />%s</p>' % (SITE["role"], meta_text(SITE["person"])),
        ('        <div class="footer-social">%s</div>' % social) if social else '',
        '      </div>',
        '',
        '      <div class="footer-col">',
        '        <h3>Το κέντρο</h3>',
        '        <p class="footer-addr">%s</p>' % "<br />".join(contact_lines),
        '        <nav aria-label="Στοιχεία επικοινωνίας" class="footer-links">',
        '          %s' % "".join(links),
        '        </nav>',
        '        <p class="footer-hours">%s</p>' % CONTACT["hours"],
        '      </div>',
        '',
        '      <div class="footer-col">',
        '        <h3>Υπηρεσίες</h3>',
        '        <nav aria-label="Υπηρεσίες" class="footer-links">%s'
        '<a href="%sfysikotherapeftria/index.html">Η Φυσικοθεραπεύτρια</a></nav>' % (ypir, r),
        '      </div>',
        '',
        '      <div class="footer-col">',
        '        <h3>Θεραπείες</h3>',
        '        <nav aria-label="Θεραπείες" class="footer-links">%s'
        '<a href="%sepikoinonia.html">Επικοινωνία</a></nav>' % (ther, r),
        '      </div>',
        '    </div>',
        '',
        '    <p class="medical-disclaimer">Το περιεχόμενο του ιστότοπου έχει ενημερωτικό '
        'χαρακτήρα και δεν υποκαθιστά την ιατρική συμβουλή, διάγνωση ή θεραπεία. Για κάθε '
        'θέμα υγείας απευθυνθείτε στον ιατρό ή στον φυσικοθεραπευτή σας.</p>',
        '',
        '    <div class="footer-bottom">',
        '      <p class="footer-copy">© <span id="year">2026</span> %s. Με επιφύλαξη '
        'παντός δικαιώματος.</p>' % meta_text(SITE["name"]),
        '      <p class="cb-credit">Made by <a href="https://clinicbrain.gr/?utm_source='
        'client-site&amp;utm_medium=footer&amp;utm_campaign=made-by" target="_blank" '
        'rel="noopener noreferrer">CLINICBRAIN</a></p>',
        '    </div>',
        '  </footer>',
        '  <script src="%smain.js" defer></script>' % r,
        '</body>',
        '</html>',
    ])


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def render_blocks(blocks):
    out = []
    for kind, value in blocks:
        if kind == "h2":
            out.append("        <h2>%s</h2>" % value)
        elif kind == "h3":
            out.append("        <h3>%s</h3>" % value)
        elif kind == "lead":
            out.append('        <p class="lead-p">%s</p>' % value)
        elif kind == "p":
            out.append("        <p>%s</p>" % value)
        elif kind == "quote":
            out.append("        <blockquote>%s</blockquote>" % value)
        elif kind in ("ticks", "ticks2"):
            cls = "ticks two-col" if kind == "ticks2" else "ticks"
            items = "".join("<li>%s</li>" % i for i in value)
            out.append('        <ul class="%s">%s</ul>' % (cls, items))
        elif kind == "numlist":
            items = "".join("<li>%s</li>" % i for i in value)
            out.append('        <ol class="numlist">%s</ol>' % items)
    return "\n".join(out)


def aside(section, page):
    """Sticky πλαινη στηλη σελιδας περιεχομενου."""
    meta = []
    if CONTACT["street"]:
        meta.append('          <p class="aside-meta"><strong>Το κέντρο</strong><br />%s<br />%s</p>'
                    % (CONTACT["street"], CONTACT["locality"] or ""))
    else:
        meta.append('          <p class="aside-meta"><strong>Διεύθυνση</strong><br />%s</p>' % TBD)

    links = "".join(
        '<a href="%s.html"%s>%s</a>'
        % (p["slug"], ' aria-current="page"' if p["slug"] == page["slug"] else '', p["title"])
        for p in section["pages"])

    return "\n".join([
        '      <aside class="svc-aside">',
        '        <div class="aside-card">',
        '          <h3>Κλείστε ραντεβού</h3>',
        '          <p>Το κέντρο δέχεται κατόπιν ραντεβού. Η πρώτη επίσκεψη αφιερώνεται '
        'στην αναλυτική αξιολόγηση.</p>',
        '          %s' % cta_primary_block(1),
        '          <a href="../epikoinonia.html" class="btn btn-ghost btn-block">Επικοινωνία</a>',
        "\n".join(meta),
        '        </div>',
        '        <div class="aside-card">',
        '          <h3>%s</h3>' % section["title"],
        '          <nav class="aside-links" aria-label="Σχετικές σελίδες">%s</nav>' % links,
        '          <p style="margin:1rem 0 0"><a href="index.html" class="svc-more">'
        'Όλα · %s →</a></p>' % section["title"],
        '        </div>',
        '      </aside>',
    ])


# ---------------------------------------------------------------------------
# Σελιδες
# ---------------------------------------------------------------------------

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return path


def build_leaf(section, page):
    canonical = "%s/%s/%s.html" % (SITE["url"], section["slug"], page["slug"])
    title = "%s | %s" % (meta_text(page["title"]), SITE["short"])
    trail = [("Αρχική", SITE["url"] + "/"),
             (section["title"], "%s/%s/index.html" % (SITE["url"], section["slug"])),
             (page["title"], canonical)]
    html = [
        head(title, page["lead"], canonical, 1, breadcrumb_schema(trail)),
        nav(1, section["slug"], page["slug"]),
        '  <main id="main">',
        '<nav class="crumbs container" aria-label="Διαδρομή">'
        '<a href="../index.html">Αρχική</a><span class="sep">/</span>'
        '<a href="index.html">%s</a><span class="sep">/</span>'
        '<span aria-current="page">%s</span></nav>' % (section["title"], page["title"]),
        '    <section class="page-hero" data-mark="%s">' % section["mark"],
        '      <div class="container">',
        '        <p class="eyebrow">%s</p>' % section["title"],
        '        <h1 class="page-title">%s</h1>' % page["title"],
        '        <p class="page-lead">%s</p>' % page["lead"],
        '      </div>',
        '    </section>',
        '',
        '    <section class="svc-detail">',
        '      <div class="container svc-detail-grid">',
        '        <article class="svc-body">',
        render_blocks(page["blocks"]),
        '        </article>',
        aside(section, page),
        '      </div>',
        '    </section>',
        '  </main>',
        cta_band(1),
        footer(1),
    ]
    return write("%s/%s.html" % (section["slug"], page["slug"]), "\n".join(html) + "\n")


def build_hub(section):
    canonical = "%s/%s/index.html" % (SITE["url"], section["slug"])
    title = "%s | %s" % (meta_text(section["title"]), SITE["short"])
    trail = [("Αρχική", SITE["url"] + "/"), (section["title"], canonical)]

    cards = []
    for i, page in enumerate(section["pages"], start=1):
        cards += [
        '        <a class="svc reveal" href="%s.html">' % page["slug"],
        '          <span class="svc-num">%02d</span>' % i,
        '          <h3>%s</h3>' % page["title"],
        '          <p>%s</p>' % page["lead"],
        '          <span class="svc-more">Μάθετε περισσότερα →</span>',
        '        </a>',
        ]

    html = [
        head(title, section["lead"], canonical, 1, breadcrumb_schema(trail)),
        nav(1, section["slug"]),
        '  <main id="main">',
        '<nav class="crumbs container" aria-label="Διαδρομή">'
        '<a href="../index.html">Αρχική</a><span class="sep">/</span>'
        '<span aria-current="page">%s</span></nav>' % section["title"],
        '    <section class="page-hero" data-mark="%s">' % section["mark"],
        '      <div class="container">',
        '        <p class="eyebrow">%s</p>' % section["eyebrow"],
        '        <h1 class="page-title">%s</h1>' % section["title"],
        '        <p class="page-lead">%s</p>' % section["lead"],
        '      </div>',
        '    </section>',
        '    <section class="services services--hub">',
        '      <div class="container">',
        '        <div class="services-grid">',
        "\n".join(cards),
        '        </div>',
        '      </div>',
        '    </section>',
        '  </main>',
        cta_band(1),
        footer(1),
    ]
    return write("%s/index.html" % section["slug"], "\n".join(html) + "\n")


def build_home():
    canonical = SITE["url"] + "/index.html"
    sec = {s["slug"]: s for s in SECTIONS}

    strip = "".join('<span>%s</span><span class="dot">•</span>' % w
                    for w in STRIP_WORDS * 2)

    svc_cards = []
    for i, (sslug, pslug, icon) in enumerate(HOME_SERVICES, start=1):
        page = next(p for p in sec[sslug]["pages"] if p["slug"] == pslug)
        svc_cards += [
        '        <a class="svc reveal" href="%s/%s.html">' % (sslug, pslug),
        '          <span class="svc-icon" aria-hidden="true">%s</span>' % icon,
        '          <span class="svc-num">%02d</span>' % i,
        '          <h3>%s</h3>' % page["title"],
        '          <p>%s</p>' % page["lead"],
        '          <span class="svc-more">Μάθετε περισσότερα →</span>',
        '        </a>',
        ]

    stats = "".join('<div class="stat"><span class="stat-n">%s</span>'
                    '<span class="stat-l">%s</span></div>' % (n, l) for n, l in HOME_STATS)
    steps = "".join('<div class="step reveal"><span class="step-n">%s</span><h3>%s</h3>'
                    '<p>%s</p></div>' % s for s in HOME_STEPS)
    creds = "".join('<div class="cred"><span class="cred-k">%s</span>'
                    '<span class="cred-v">%s</span></div>' % c for c in HOME_CREDS)

    ther_cards = []
    for i, page in enumerate(sec["therapeies"]["pages"], start=1):
        ther_cards += [
        '        <a class="svc reveal" href="therapeies/%s.html">' % page["slug"],
        '          <span class="svc-num">%02d</span>' % i,
        '          <h3>%s</h3>' % page["title"],
        '          <p>%s</p>' % page["lead"],
        '          <span class="svc-more">Μάθετε περισσότερα →</span>',
        '        </a>',
        ]

    html = [
        head(HOME_META["title"], HOME_META["description"], canonical, 0,
             keywords=HOME_META["keywords"]),
        nav(0, home=True),
        '  <main id="main">',
        '    <section class="hero" id="hero">',
        '      <div class="hero-inner container">',
        '        <p class="eyebrow reveal">%s</p>' % SITE["tagline"],
        '        <h1 class="hero-title reveal">Elite Physiotherapy<br /><em>by Tatiana Gkouwir</em></h1>',
        '        <p class="hero-lead reveal">Σύγχρονο κέντρο φυσικοθεραπείας και αποκατάστασης, '
        'με εξειδικευμένες θεραπείες σε μυοσκελετικά και νευρολογικά προβλήματα — λεπτομερής '
        'αξιολόγηση, κλινικός συλλογισμός και ένα πλάνο φτιαγμένο για τη δική σας περίπτωση.</p>',
        '        <div class="hero-actions reveal">',
        '          %s' % cta_primary(0),
        '          <a href="#services" class="btn btn-ghost">Οι Υπηρεσίες μας</a>',
        '        </div>',
        '      </div>',
        '      <div class="hero-scroll" aria-hidden="true"><span></span></div>',
        '    </section>',
        '',
        '    <div class="strip" aria-hidden="true">',
        '      <div class="strip-track">%s</div>' % strip,
        '    </div>',
        '',
        '    <section class="about" id="about">',
        '      <div class="container about-grid">',
        '        <div class="about-media reveal">',
        '          <img src="%s" alt="%s — λογότυπο" width="1074" height="938" />'
        % (SITE["logo"], esc_attr(SITE["name"])),
        '          <div class="about-badge">',
        '            <span class="about-badge-num">Π.Σ.Φ.</span>',
        '            <span class="about-badge-label">Μέλος Πανελληνίου<br />Συλλόγου Φυσικοθεραπευτών</span>',
        '          </div>',
        '        </div>',
        '        <div class="about-copy">',
        '          <p class="eyebrow reveal">Η Φυσικοθεραπεύτρια</p>',
        '          <h2 class="section-title reveal">Τατιάνα Γκουβίρ, <em>Φυσικοθεραπεύτρια</em></h2>',
        '          <p class="about-role reveal">Πτυχιούχος Φυσικοθεραπείας Α.Τ.Ε.Ι.Θ. · Μέλος Π.Σ.Φ.</p>',
        '          <ul class="about-creds reveal">'
        '<li>Πτυχιούχος του τμήματος Φυσικοθεραπείας του Αλεξάνδρειου Τεχνολογικού '
        'Εκπαιδευτικού Ιδρύματος Θεσσαλονίκης (Α.Τ.Ε.Ι.Θ., 2017).</li>'
        '<li>Μέλος του Πανελληνίου Συλλόγου Φυσικοθεραπευτών.</li>'
        '<li>Κλινική εμπειρία σε ιδιωτικά κέντρα φυσικοθεραπείας, με κύριο αντικείμενο τις '
        'αθλητικές κακώσεις και τις εξειδικευμένες τεχνικές αντιμετώπισής τους.</li>'
        '<li>Μετεκπαίδευση στο Manual Therapy από τον Σύλλογο Φυσικοθεραπευτών &amp; '
        'Χειροθεραπευτών Ελλάδος (A.M.P.G.).</li>'
        '<li>Πιστοποιήσεις σε Mulligan Therapy και Dry Needling (David G. Simons Academy).</li>'
        '<li>BSPTS – Concept by Rigo για τη σκολίωση και τις παθήσεις της σπονδυλικής στήλης.</li>'
        '</ul>',
        '          <a href="fysikotherapeftria/viografiko.html" class="btn btn-ghost reveal">'
        'Το πλήρες βιογραφικό →</a>',
        '        </div>',
        '      </div>',
        '    </section>',
        '',
        '    <section class="stats">',
        '      <div class="container">',
        '        <div class="stats-grid reveal">%s</div>' % stats,
        '      </div>',
        '    </section>',
        '',
        '    <section class="services" id="services">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Υπηρεσίες</p>',
        '          <h2 class="section-title">Εξειδικευμένη αποκατάσταση,<br />σε κάθε φάση</h2>',
        '          <p>Από τον οξύ μυοσκελετικό πόνο και τις αθλητικές κακώσεις, έως τη '
        'μετεγχειρητική αποκατάσταση, τη σκολίωση και τα ειδικά περιστατικά.</p>',
        '        </div>',
        '        <div class="services-grid">',
        "\n".join(svc_cards),
        '        </div>',
        '      </div>',
        '    </section>',
        '',
        '    <section class="process">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Η προσέγγισή μας</p>',
        '          <h2 class="section-title">Τέσσερα καθαρά βήματα</h2>',
        '        </div>',
        '        <div class="steps">%s</div>' % steps,
        '      </div>',
        '    </section>',
        '',
        '    <section class="philosophy">',
        '      <div class="container philosophy-inner">',
        '        <span class="philosophy-mark" aria-hidden="true">“</span>',
        '        <blockquote>Η λεπτομερής αξιολόγηση και ο <em>κλινικός συλλογισμός</em> '
        'αποτελούν τις βάσεις με τις οποίες ο θεραπευόμενος θα λάβει το βέλτιστο '
        'εξατομικευμένο πλάνο αποκατάστασης.</blockquote>',
        '        <cite class="philosophy-cite">Elite Physiotherapy</cite>',
        '      </div>',
        '    </section>',
        '',
        '    <section class="services" id="therapies">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Θεραπείες &amp; Τεχνικές</p>',
        '          <h2 class="section-title">Σύγχρονα μέσα,<br />επιλεγμένα με κριτήριο</h2>',
        '          <p>Κάθε τεχνική επιλέγεται με βάση την αξιολόγηση — όχι ως πακέτο, αλλά ως '
        'απάντηση σε ένα συγκεκριμένο εύρημα.</p>',
        '        </div>',
        '        <div class="services-grid">',
        "\n".join(ther_cards),
        '        </div>',
        '      </div>',
        '    </section>',
        '',
        '    <section class="creds">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Τίτλοι &amp; Μετεκπαιδεύσεις</p>',
        '          <h2 class="section-title">Τεκμηριωμένη εκπαίδευση,<br />σε κάθε τεχνική</h2>',
        '        </div>',
        '        <div class="creds-grid reveal">%s</div>' % creds,
        '        <p class="quotes-note"><a href="fysikotherapeftria/metekpaideuseis.html" '
        'class="svc-more">Όλες οι μετεκπαιδεύσεις &amp; τα σεμινάρια →</a></p>',
        '      </div>',
        '    </section>',
        '  </main>',
        cta_band(0),
        footer(0),
    ]
    return write("index.html", "\n".join(html) + "\n")


def build_contact():
    canonical = SITE["url"] + "/epikoinonia.html"
    title = "Επικοινωνία | %s" % SITE["short"]
    desc = ("Επικοινωνήστε με το Elite Physiotherapy by Tatiana Gkouwir — Κέντρο "
            "Φυσικοθεραπείας και Αποκατάστασης. Ραντεβού κατόπιν επικοινωνίας.")
    trail = [("Αρχική", SITE["url"] + "/"), ("Επικοινωνία", canonical)]

    rows = []
    rows.append(('Τηλέφωνο',
                 '<a href="tel:%s">%s</a>' % (CONTACT["phone"], CONTACT["phone_label"])
                 if CONTACT["phone"] else TBD))
    if CONTACT["mobile"]:
        rows.append(('Κινητό', '<a href="tel:%s">%s</a>'
                     % (CONTACT["mobile"], CONTACT["mobile_label"])))
    rows.append(('Email',
                 '<a href="mailto:%s">%s</a>' % (CONTACT["email"], CONTACT["email"])
                 if CONTACT["email"] else TBD))
    if CONTACT["street"]:
        addr = CONTACT["street"]
        if CONTACT["locality"]:
            addr += "<br />%s" % CONTACT["locality"]
        if CONTACT["postal"]:
            addr += ", Τ.Κ. %s" % CONTACT["postal"]
    else:
        addr = TBD
    rows.append(('Διεύθυνση', addr))
    rows.append(('Ωράριο', CONTACT["hours"]))

    rows_html = "".join(
        '<li><span class="contact-label">%s</span><span class="contact-value">%s</span></li>'
        % (k, v) for k, v in rows)

    if CONTACT["maps"]:
        map_html = ('<div class="contact-map reveal"><iframe src="%s" loading="lazy" '
                    'title="Χάρτης — Elite Physiotherapy" referrerpolicy='
                    '"no-referrer-when-downgrade"></iframe></div>' % CONTACT["maps"])
    else:
        map_html = ('<div class="reveal"><div class="notice"><strong>Χάρτης και διεύθυνση.</strong>'
                    '<br />Ο χάρτης θα ενεργοποιηθεί μόλις οριστικοποιηθεί η διεύθυνση του '
                    'κέντρου. Για ραντεβού ή πληροφορίες, επικοινωνήστε μαζί μας.</div></div>')

    html = [
        head(title, desc, canonical, 0, breadcrumb_schema(trail)),
        nav(0, "epikoinonia"),
        '  <main id="main">',
        '<nav class="crumbs container" aria-label="Διαδρομή">'
        '<a href="index.html">Αρχική</a><span class="sep">/</span>'
        '<span aria-current="page">Επικοινωνία</span></nav>',
        '    <section class="page-hero" data-mark="◆">',
        '      <div class="container">',
        '        <p class="eyebrow">Επικοινωνία</p>',
        '        <h1 class="page-title">Κλείστε το ραντεβού σας</h1>',
        '        <p class="page-lead">Το κέντρο δέχεται κατόπιν ραντεβού. Η πρώτη επίσκεψη '
        'αφιερώνεται στην αναλυτική αξιολόγηση, ώστε να σχεδιαστεί το πλάνο αποκατάστασης '
        'που ταιριάζει στη δική σας περίπτωση.</p>',
        '      </div>',
        '    </section>',
        '    <section class="contact">',
        '      <div class="container contact-grid">',
        '        <div>',
        '          <p class="contact-note">Συμπληρώστε τα στοιχεία σας ή καλέστε μας για να '
        'κανονίσουμε την πρώτη σας συνεδρία. <strong>Θα χαρούμε να απαντήσουμε σε κάθε '
        'ερώτησή σας.</strong></p>',
        '          <ul class="contact-list">%s</ul>' % rows_html,
        '          <div class="contact-actions">',
        '            %s' % cta_primary(0),
        '            <a href="ypiresies/index.html" class="btn btn-ghost">Οι υπηρεσίες μας</a>',
        '          </div>',
        '        </div>',
        '        %s' % map_html,
        '      </div>',
        '    </section>',
        '  </main>',
        cta_band(0),
        footer(0),
    ]
    return write("epikoinonia.html", "\n".join(html) + "\n")


def build_sitemap(paths):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in paths:
        if path == "index.html":
            loc, prio = SITE["url"] + "/", "1.0"
        elif path.endswith("/index.html"):
            loc, prio = "%s/%s" % (SITE["url"], path), "0.8"
        else:
            loc, prio = "%s/%s" % (SITE["url"], path), "0.6"
        lines.append('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                     '<changefreq>monthly</changefreq><priority>%s</priority></url>'
                     % (loc, SITE["lastmod"], prio))
    lines.append('</urlset>')
    write("sitemap.xml", "\n".join(lines) + "\n")

    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["url"])


def copy_logo():
    """Αντιγραφη του logo στο assets/, αν υπαρχει πηγη."""
    dest = os.path.join(ROOT, SITE["logo"])
    if os.path.exists(dest):
        return
    for candidate in (os.path.join(ROOT, "_build", "logo.jpg"),
                      os.path.expanduser("~/Desktop/tatiana/logo.jpg")):
        if os.path.exists(candidate):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(candidate, dest)
            print("  logo -> %s" % SITE["logo"])
            return
    print("  ! ΠΡΟΣΟΧΗ: δεν βρέθηκε το %s" % SITE["logo"])


def main():
    copy_logo()
    paths = [build_home(), build_contact()]
    for section in SECTIONS:
        paths.append(build_hub(section))
        for page in section["pages"]:
            paths.append(build_leaf(section, page))
    build_sitemap(paths)
    print("Παρήχθησαν %d σελίδες + sitemap.xml + robots.txt" % len(paths))
    for p in paths:
        print("  " + p)


if __name__ == "__main__":
    main()

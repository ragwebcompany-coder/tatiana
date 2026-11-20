# -*- coding: utf-8 -*-
"""
Generator για το site του Elite Physiotherapy by Tatiana Gkouwir.

    python _build/build.py

Παραγει: index.html, epikoinonia.html, τις ενοτητες, sitemap.xml, robots.txt.
Ολο το περιεχομενο ζει στο _build/structure.py.
"""

import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from structure import (  # noqa: E402
    SITE, CONTACT, TBD, SECTIONS, HOME_SERVICES, HOME_STATS, HOME_CREDS,
    HOME_STEPS, STRIP_WORDS, HOME_META,
    PHOTO_DIR, PHOTO_PORTRAIT, PHOTOS, HOME_PORTRAIT, HOME_SPACE,
    PHOTO_ALT, CARD_PHOTOS, HOME_HERO, HOME_PROCESS, HOME_GALLERY, CONTACT_PHOTO,
    ABOUT_TYPE, CREDENTIALS, FAQS,
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


def esc_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clip(text, limit=158):
    """Περιγραφη εως ~158 χαρακτηρες, κομμενη σε οριο λεξης."""
    text = meta_text(text)
    if len(text) <= limit:
        return text
    return text[:limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:·—-(") + "…"


def asset_version(name):
    """Συντομο hash του αρχειου, για ?v= (μακρυ cache χωρις μπαγιατικα αρχεια)."""
    with open(os.path.join(ROOT, name), "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()[:8]


def photo_url(name):
    return "%s/%s/%s.webp" % (SITE["url"], PHOTO_DIR, name)


def with_place(title):
    """Προσθετει την περιοχη στον τιτλο, οταν εχει οριστει (π.χ. «στη Γλυφάδα»)."""
    return "%s %s" % (title, CONTACT["locality_in"]) if CONTACT.get("locality_in") else title


CLINIC_ID = SITE["url"] + "/#clinic"
PERSON_ID = SITE["url"] + "/#tatiana-gkouvir"
WEBSITE_ID = SITE["url"] + "/#website"
DEFAULT_IMAGE = HOME_HERO[0]


def ld(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


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
    """Βασικο γραφημα καθε σελιδας: κεντρο + φυσικοθεραπευτρια + website."""
    clinic = {
        "@type": ["Physiotherapy", "MedicalBusiness"],
        "@id": CLINIC_ID,
        "name": meta_text(SITE["name"]),
        "alternateName": SITE["short"],
        "description": meta_text(HOME_META["description"]),
        "url": SITE["url"] + "/",
        "image": [photo_url(n) for n, _ in HOME_SPACE],
        "logo": SITE["url"] + "/" + SITE["logo"],
        "medicalSpecialty": "Physiotherapy",
        "knowsLanguage": ["el", "en"],
        "founder": {"@id": PERSON_ID},
        "employee": {"@id": PERSON_ID},
        "availableService": [],
    }
    for section in SECTIONS:
        if section["slug"] == "fysikotherapeftria":
            continue
        for page in section["pages"]:
            key = "%s/%s" % (section["slug"], page["slug"])
            kind = ABOUT_TYPE.get(key, "PhysicalTherapy")
            clinic["availableService"].append({
                "@type": "MedicalTherapy" if kind == "MedicalCondition" else kind,
                "name": meta_text(page["title"]),
                "url": "%s/%s.html" % (SITE["url"], key),
            })
    if CONTACT["phone"]:
        clinic["telephone"] = CONTACT["phone"]
        clinic["contactPoint"] = [{"@type": "ContactPoint", "contactType": "appointments",
                                   "telephone": CONTACT["phone"],
                                   "availableLanguage": ["el", "en"]}]
    if CONTACT["email"]:
        clinic["email"] = CONTACT["email"]
    if CONTACT["street"]:
        addr = {"@type": "PostalAddress", "streetAddress": CONTACT["street"],
                "addressCountry": "GR"}
        if CONTACT["locality"]:
            addr["addressLocality"] = CONTACT["locality"]
        if CONTACT["postal"]:
            addr["postalCode"] = CONTACT["postal"]
        if CONTACT.get("region"):
            addr["addressRegion"] = CONTACT["region"]
        clinic["address"] = addr
    if CONTACT.get("lat") and CONTACT.get("lng"):
        clinic["geo"] = {"@type": "GeoCoordinates",
                         "latitude": CONTACT["lat"], "longitude": CONTACT["lng"]}
    if CONTACT.get("maps_url"):
        clinic["hasMap"] = CONTACT["maps_url"]
    if CONTACT["social"]:
        clinic["sameAs"] = [u for _, u in CONTACT["social"]]

    person = {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": meta_text(SITE["person"]),
        "alternateName": "Tatiana Gkouwir",
        "jobTitle": SITE["role"],
        "description": meta_text(SECTIONS[0]["lead"]),
        "url": SITE["url"] + "/fysikotherapeftria/viografiko.html",
        "image": photo_url(PHOTOS["fysikotherapeftria/viografiko"]["lead"][0]),
        "worksFor": {"@id": CLINIC_ID},
        "knowsLanguage": ["el", "en"],
        "alumniOf": {"@type": "CollegeOrUniversity",
                     "name": "Αλεξάνδρειο Τεχνολογικό Εκπαιδευτικό Ίδρυμα Θεσσαλονίκης"},
        "memberOf": {"@type": "Organization",
                     "name": "Πανελλήνιος Σύλλογος Φυσικοθεραπευτών"},
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "name": name,
             "recognizedBy": {"@type": "Organization", "name": org}}
            for name, org in CREDENTIALS],
        "knowsAbout": [meta_text(p["title"]) for sec in SECTIONS[1:] for p in sec["pages"]],
    }
    website = {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE["url"] + "/",
               "name": meta_text(SITE["name"]), "inLanguage": "el",
               "publisher": {"@id": CLINIC_ID}}
    return ld({"@context": "https://schema.org", "@graph": [clinic, person, website]})


def page_schema(section, page, canonical, photos):
    """Schema σελιδας περιεχομενου· δειχνει στα @id του βασικου γραφηματος."""
    key = "%s/%s" % (section["slug"], page["slug"])
    data = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "@id": canonical, "url": canonical,
        "name": meta_text(page["title"]),
        "description": meta_text(page["lead"]),
        "inLanguage": "el",
        "isPartOf": {"@id": WEBSITE_ID},
        "datePublished": SITE["published"], "dateModified": SITE["lastmod"],
        "author": {"@id": PERSON_ID},
        "reviewedBy": {"@id": PERSON_ID},
        "publisher": {"@id": CLINIC_ID},
        "hasPart": [{"@type": "WebPageElement", "name": meta_text(v), "position": i}
                    for i, v in enumerate((v for k, v in page["blocks"] if k == "h2"), start=1)],
    }
    if photos and photos.get("lead"):
        data["primaryImageOfPage"] = photo_url(photos["lead"][0])
    if key == "fysikotherapeftria/viografiko":
        data["@type"] = "ProfilePage"
        data["mainEntity"] = {"@id": PERSON_ID}
        del data["author"], data["reviewedBy"]
    elif section["slug"] == "fysikotherapeftria":
        data["about"] = {"@id": PERSON_ID}
    else:
        data["about"] = {"@type": ABOUT_TYPE.get(key, "PhysicalTherapy"),
                         "name": meta_text(page["title"])}
    return ld(data)


def faq_schema(key, canonical):
    return ld({"@context": "https://schema.org", "@type": "FAQPage",
               "@id": canonical + "#faq", "inLanguage": "el",
               "mainEntity": [{"@type": "Question", "name": q,
                               "acceptedAnswer": {"@type": "Answer", "text": a}}
                              for q, a in FAQS[key]]})


def breadcrumb_schema(trail):
    items = []
    for i, (name, href) in enumerate(trail, start=1):
        items.append({"@type": "ListItem", "position": i,
                      "name": meta_text(name), "item": href})
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
               "itemListElement": items})


# ---------------------------------------------------------------------------
# Head / Nav / Footer
# ---------------------------------------------------------------------------

def head(title, description, canonical, depth, extra_ld=None, keywords=None,
         image=None, og_type="website"):
    r = up(depth)
    desc = clip(description).replace("&", "&amp;").replace('"', "&quot;")
    image = image or DEFAULT_IMAGE
    img_w, img_h = (1200, 1800) if image in PHOTO_PORTRAIT else (1800, 1200)
    if extra_ld is None:
        extra_ld = []
    elif not isinstance(extra_ld, (list, tuple)):
        extra_ld = [extra_ld]
    parts = [
        '<!DOCTYPE html>', '<html lang="el">', '<head>',
        '  <meta charset="UTF-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        '  <title>%s</title>' % title,
        '  <meta name="description" content="%s" />' % desc,
    ]
    if keywords:
        parts.append('  <meta name="keywords" content="%s" />' % esc_attr(keywords))
    parts += [
        '  <meta name="author" content="%s" />' % esc_attr(SITE["person"]),
        '  <meta name="robots" content="index, follow, max-image-preview:large, '
        'max-snippet:-1, max-video-preview:-1" />',
        '  <meta name="theme-color" content="#1e3a5f" />',
        '  <link rel="canonical" href="%s" />' % canonical,
    ]
    if CONTACT.get("lat") and CONTACT.get("lng"):
        parts += [
            '  <meta name="geo.region" content="GR" />',
            '  <meta name="geo.placename" content="%s" />' % esc_attr(CONTACT["locality"] or ""),
            '  <meta name="geo.position" content="%s;%s" />' % (CONTACT["lat"], CONTACT["lng"]),
            '  <meta name="ICBM" content="%s, %s" />' % (CONTACT["lat"], CONTACT["lng"]),
        ]
    parts += [
        '',
        '  <meta property="og:site_name" content="%s" />' % esc_attr(SITE["name"]),
        '  <meta property="og:locale" content="el_GR" />',
        '  <meta property="og:type" content="%s" />' % og_type,
        '  <meta property="og:title" content="%s" />' % esc_attr(title),
        '  <meta property="og:description" content="%s" />' % desc,
        '  <meta property="og:url" content="%s" />' % canonical,
        '  <meta property="og:image" content="%s" />' % photo_url(image),
        '  <meta property="og:image:width" content="%d" />' % img_w,
        '  <meta property="og:image:height" content="%d" />' % img_h,
        '  <meta property="og:image:alt" content="%s" />' % esc_attr(PHOTO_ALT[image]),
        '  <meta name="twitter:card" content="summary_large_image" />',
        '',
        '  <link rel="icon" type="image/jpeg" href="%s%s" />' % (r, SITE["logo"]),
        '  <link rel="apple-touch-icon" href="%s%s" />' % (r, SITE["logo"]),
        '  <link rel="preconnect" href="https://fonts.googleapis.com" />',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
        '  <link rel="preload" as="style" href="%s" />' % FONTS,
        '  <link href="%s" rel="stylesheet" media="print" onload="this.media=\'all\'" />' % FONTS,
        '  <noscript><link href="%s" rel="stylesheet" /></noscript>' % FONTS,
        '  <link rel="stylesheet" href="%sstyles.css?v=%s" />' % (r, asset_version("styles.css")),
        '  <script type="application/ld+json">%s</script>' % business_schema(),
    ]
    for block in extra_ld:
        parts.append('  <script type="application/ld+json">%s</script>' % block)
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
        '      <p class="cb-credit">Made by <a href="https://astramarketing.gr/?utm_source='
        'client-site&amp;utm_medium=footer&amp;utm_campaign=made-by" target="_blank" '
        'rel="noopener noreferrer">astra</a></p>',
        '    </div>',
        '  </footer>',
        '  <script src="%smain.js?v=%s" defer></script>' % (r, asset_version("main.js")),
        '</body>',
        '</html>',
    ])


# ---------------------------------------------------------------------------
# Φωτογραφιες
# ---------------------------------------------------------------------------

def photo_img(name, alt, depth, sizes, cls="", lazy=True):
    """<img> με μικρη (900px) και μεγαλη (1800px) εκδοχη."""
    base = "%s%s/%s" % (up(depth), PHOTO_DIR, name)
    w, h = (1200, 1800) if name in PHOTO_PORTRAIT else (1800, 1200)
    return ('<img src="%s-sm.webp" srcset="%s-sm.webp %dw, %s.webp %dw" sizes="%s" '
            'alt="%s" width="%d" height="%d"%s%s />'
            % (base, base, w // 2, base, w, sizes, esc_attr(alt), w, h,
               (' class="%s"' % cls) if cls else '',
               ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'))


def photo_link(name, alt, depth, sizes, cls="", lazy=True):
    """Φωτογραφια που ανοιγει σε μεγεθυνση (βλ. lightbox στο main.js)."""
    classes = "zoom" + (" tall" if name in PHOTO_PORTRAIT else "") + ((" " + cls) if cls else "")
    return ('<a class="%s" href="%s%s/%s.webp" aria-label="Μεγέθυνση: %s">%s</a>'
            % (classes, up(depth), PHOTO_DIR, name, esc_attr(alt),
               photo_img(name, alt, depth, sizes, lazy=lazy)))


def card_thumb(section_slug, page_slug, depth):
    """Μικρογραφια στην κορυφη μιας καρτας."""
    key = "%s/%s" % (section_slug, page_slug)
    name = CARD_PHOTOS.get(key) or (PHOTOS[key]["lead"][0] if key in PHOTOS else None)
    if not name:
        return ""
    cls = "tall" if name in PHOTO_PORTRAIT else ""
    return ('          <span class="svc-thumb %s">%s</span>'
            % (cls, photo_img(name, "", depth, "(max-width: 620px) 94vw, 380px")))


def photo_tiles(names, depth, sizes="(max-width: 620px) 94vw, 380px"):
    return "".join(photo_link(n, PHOTO_ALT[n], depth, sizes) for n in names)


def lead_figure(photos, depth):
    if not photos or not photos.get("lead"):
        return ""
    name, alt = photos["lead"]
    portrait = name in PHOTO_PORTRAIT
    sizes = "(max-width: 620px) 70vw, 320px" if portrait else "(max-width: 820px) 94vw, 760px"
    return ('        <figure class="lead-figure%s">%s</figure>'
            % (" portrait" if portrait else "",
               photo_link(name, alt, depth, sizes, lazy=False)))


def gallery(photos, depth):
    if not photos or not photos.get("gallery"):
        return ""
    # Οι καθετες πρωτες: πιανουν δυο σειρες και διπλα τους στοιβαζονται δυο οριζοντιες.
    tall = [i for i in photos["gallery"] if i[0] in PHOTO_PORTRAIT]
    wide = [i for i in photos["gallery"] if i[0] not in PHOTO_PORTRAIT]
    items = tall + wide
    all_tall = not wide
    sizes = "(max-width: 620px) 94vw, 380px"
    # Μονος αριθμος κελιων αφηνει κενο: η τελευταια οριζοντια το γεμιζει.
    extra = {}
    if wide and (2 * len(tall) + len(wide)) % 2:
        extra[wide[-1][0]] = "fill" if (len(tall), len(wide)) == (1, 1) else "wide"
    tiles = "".join(photo_link(n, a, depth, sizes, cls=extra.get(n, "")) for n, a in items)
    return "\n".join([
        '        <h2 class="gallery-title">Φωτογραφίες από το κέντρο</h2>',
        '        <div class="gallery%s">%s</div>' % (" gallery--tall" if all_tall else "", tiles),
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


def faq_block(key):
    if key not in FAQS:
        return ""
    items = "".join('<details><summary>%s</summary><p>%s</p></details>'
                    % (esc_html(q), esc_html(a)) for q, a in FAQS[key])
    return "\n".join(['        <h2 class="faq-title" id="faq">Συχνές ερωτήσεις</h2>',
                      '        <div class="faq">%s</div>' % items])


def byline(section):
    href = "viografiko.html" if section["slug"] == "fysikotherapeftria" \
        else "../fysikotherapeftria/viografiko.html"
    return ('        <p class="byline">Επιμέλεια κειμένου: <a href="%s">%s</a>, %s, μέλος του '
            'Πανελληνίου Συλλόγου Φυσικοθεραπευτών. Τελευταία ενημέρωση: '
            '<time datetime="%s">%s</time>.</p>'
            % (href, meta_text(SITE["person"]), SITE["role"], SITE["lastmod"],
               SITE["lastmod_label"]))


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
    key = "%s/%s" % (section["slug"], page["slug"])
    name = page["title"] if section["slug"] == "fysikotherapeftria" else with_place(page["title"])
    title = "%s | %s" % (name, SITE["short"])
    trail = [("Αρχική", SITE["url"] + "/"),
             (section["title"], "%s/%s/" % (SITE["url"], section["slug"])),
             (page["title"], canonical)]
    photos = PHOTOS.get(key)
    body = [b for b in (lead_figure(photos, 1), render_blocks(page["blocks"]),
                        faq_block(key), gallery(photos, 1), byline(section)) if b]
    schemas = [breadcrumb_schema(trail), page_schema(section, page, canonical, photos)]
    if key in FAQS:
        schemas.append(faq_schema(key, canonical))
    html = [
        head(title, page["lead"], canonical, 1, schemas,
             image=photos["lead"][0] if photos else None, og_type="article"),
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
        "\n".join(body),
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
    canonical = "%s/%s/" % (SITE["url"], section["slug"])
    title = "%s | %s" % (meta_text(section["title"]), SITE["short"])
    trail = [("Αρχική", SITE["url"] + "/"), (section["title"], canonical)]

    cards = []
    for i, page in enumerate(section["pages"], start=1):
        cards += [
        '        <a class="svc reveal" href="%s.html">' % page["slug"],
        card_thumb(section["slug"], page["slug"], 1),
        '          <span class="svc-num">%02d</span>' % i,
        '          <h2>%s</h2>' % page["title"],
        '          <p>%s</p>' % page["lead"],
        '          <span class="svc-more">Μάθετε περισσότερα →</span>',
        '        </a>',
        ]

    collection = ld({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "@id": canonical, "url": canonical, "name": meta_text(section["title"]),
        "description": meta_text(section["lead"]), "inLanguage": "el",
        "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": CLINIC_ID},
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": meta_text(pg["title"]),
             "url": "%s/%s/%s.html" % (SITE["url"], section["slug"], pg["slug"])}
            for i, pg in enumerate(section["pages"], start=1)]},
    })
    first = PHOTOS.get("%s/%s" % (section["slug"], section["pages"][0]["slug"]))
    title = "%s | %s" % (meta_text(section["title"]) if section["slug"] == "fysikotherapeftria"
                         else with_place(meta_text(section["title"])), SITE["short"])

    html = [
        head(title, section["lead"], canonical, 1, [breadcrumb_schema(trail), collection],
             image=first["lead"][0] if first else None),
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
    canonical = SITE["url"] + "/"
    sec = {s["slug"]: s for s in SECTIONS}
    webpage = ld({"@context": "https://schema.org", "@type": "WebPage",
                  "@id": canonical + "#webpage", "url": canonical,
                  "name": meta_text(HOME_META["title"]), "inLanguage": "el",
                  "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": CLINIC_ID},
                  "primaryImageOfPage": photo_url(DEFAULT_IMAGE),
                  "dateModified": SITE["lastmod"]})

    strip = "".join('<span>%s</span><span class="dot">•</span>' % w
                    for w in STRIP_WORDS * 2)

    svc_cards = []
    for i, (sslug, pslug, icon) in enumerate(HOME_SERVICES, start=1):
        page = next(p for p in sec[sslug]["pages"] if p["slug"] == pslug)
        svc_cards += [
        '        <a class="svc reveal" href="%s/%s.html">' % (sslug, pslug),
        card_thumb(sslug, pslug, 0)
        or '          <span class="svc-icon" aria-hidden="true">%s</span>' % icon,
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
        card_thumb("therapeies", page["slug"], 0),
        '          <span class="svc-num">%02d</span>' % i,
        '          <h3>%s</h3>' % page["title"],
        '          <p>%s</p>' % page["lead"],
        '          <span class="svc-more">Μάθετε περισσότερα →</span>',
        '        </a>',
        ]

    html = [
        head(HOME_META["title"], HOME_META["description"], canonical, 0, webpage,
             keywords=HOME_META["keywords"]),
        nav(0, home=True),
        '  <main id="main">',
        '    <section class="hero" id="hero">',
        '      <div class="hero-inner hero-split container">',
        '       <div class="hero-copy">',
        '        <h1 class="hero-h1 reveal"><span class="eyebrow">%s</span> '
        '<span class="hero-title">Elite Physiotherapy<br /><em>by Tatiana</em></span></h1>'
        % with_place(SITE["tagline"]),
        '        <p class="hero-lead reveal">Σύγχρονο κέντρο φυσικοθεραπείας και αποκατάστασης, '
        'με εξειδικευμένες θεραπείες σε μυοσκελετικά και νευρολογικά προβλήματα — λεπτομερής '
        'αξιολόγηση, κλινικός συλλογισμός και ένα πλάνο φτιαγμένο για τη δική σας περίπτωση.</p>',
        '        <div class="hero-actions reveal">',
        '          %s' % cta_primary(0),
        '          <a href="#services" class="btn btn-ghost">Οι Υπηρεσίες μας</a>',
        '        </div>',
        '       </div>',
        '       <div class="hero-photos reveal">%s%s</div>' % (
            photo_img(HOME_HERO[0], PHOTO_ALT[HOME_HERO[0]], 0,
                      "(max-width: 900px) 94vw, 50vw", cls="hero-photo-main", lazy=False),
            photo_img(HOME_HERO[1], PHOTO_ALT[HOME_HERO[1]], 0,
                      "(max-width: 900px) 50vw, 300px", cls="hero-photo-sub", lazy=False)),
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
        '          %s' % photo_img(HOME_PORTRAIT[0], HOME_PORTRAIT[1], 0,
                                   "(max-width: 900px) 420px, 40vw", cls="about-photo"),
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
        '    <section class="space" id="space">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Ο χώρος μας</p>',
        '          <h2 class="section-title">Ένας χώρος φτιαγμένος<br />για την αποκατάσταση</h2>',
        '          <p>Γραφείο αξιολόγησης, χώροι θεραπείας και πλήρως εξοπλισμένο γυμναστήριο '
        'θεραπευτικής άσκησης, κάτω από την ίδια στέγη.</p>',
        '        </div>',
        '        <div class="space-grid reveal">%s</div>' % "".join(
            photo_link(n, a, 0, "(max-width: 820px) 94vw, 600px") for n, a in HOME_SPACE),
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
        '        <div class="photo-row reveal">%s</div>' % photo_tiles(HOME_PROCESS, 0),
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
        '    <section class="moments" id="gallery">',
        '      <div class="container">',
        '        <div class="section-head reveal">',
        '          <p class="eyebrow">Φωτογραφίες</p>',
        '          <h2 class="section-title">Στιγμές από το κέντρο</h2>',
        '        </div>',
        '        <div class="photo-row photo-row--wrap reveal">%s</div>' % photo_tiles(HOME_GALLERY, 0),
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
        head(title, desc, canonical, 0, [breadcrumb_schema(trail), ld({
            "@context": "https://schema.org", "@type": "ContactPage", "@id": canonical,
            "url": canonical, "name": "Επικοινωνία", "inLanguage": "el",
            "isPartOf": {"@id": WEBSITE_ID}, "mainEntity": {"@id": CLINIC_ID}})],
             image=CONTACT_PHOTO),
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
        '        <div class="contact-side"><figure class="lead-figure reveal">%s</figure>%s</div>'
        % (photo_link(CONTACT_PHOTO, PHOTO_ALT[CONTACT_PHOTO], 0,
                      "(max-width: 980px) 94vw, 560px"), map_html),
        '      </div>',
        '    </section>',
        '  </main>',
        cta_band(0),
        footer(0),
    ]
    return write("epikoinonia.html", "\n".join(html) + "\n")


def sitemap_image(path):
    """Η κυρια φωτογραφια της σελιδας, για το <image:image> του sitemap."""
    if path == "index.html":
        return DEFAULT_IMAGE
    if path == "epikoinonia.html":
        return CONTACT_PHOTO
    key = path[:-5]
    if key.endswith("/index"):
        sec = next(x for x in SECTIONS if x["slug"] == key.split("/")[0])
        key = "%s/%s" % (sec["slug"], sec["pages"][0]["slug"])
    return PHOTOS[key]["lead"][0] if key in PHOTOS else None


def build_sitemap(paths):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for path in paths:
        if path == "index.html":
            loc, prio = SITE["url"] + "/", "1.0"
        elif path.endswith("/index.html"):
            loc, prio = "%s/%s" % (SITE["url"], path[:-len("index.html")]), "0.8"
        else:
            loc, prio = "%s/%s" % (SITE["url"], path), "0.6"
        img = sitemap_image(path)
        image = ('<image:image><image:loc>%s</image:loc></image:image>' % photo_url(img)) if img else ''
        lines.append('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                     '<changefreq>monthly</changefreq><priority>%s</priority>%s</url>'
                     % (loc, SITE["lastmod"], prio, image))
    lines.append('</urlset>')
    write("sitemap.xml", "\n".join(lines) + "\n")

    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["url"])


def build_llms():
    """llms.txt — συνοπτικος χαρτης του site για AI βοηθους."""
    out = ["# %s" % meta_text(SITE["name"]), "",
           "> %s" % meta_text(HOME_META["description"]), "",
           "Φυσικοθεραπεύτρια: %s, πτυχιούχος Φυσικοθεραπείας Α.Τ.Ε.Ι. Θεσσαλονίκης (2017), "
           "μέλος του Πανελληνίου Συλλόγου Φυσικοθεραπευτών." % meta_text(SITE["person"])]
    if CONTACT["street"]:
        out.append("Διεύθυνση: %s, %s %s." % (CONTACT["street"], CONTACT["locality"] or "",
                                              CONTACT["postal"] or ""))
    if CONTACT["phone"]:
        out.append("Τηλέφωνο: %s." % CONTACT["phone_label"])
    out.append("Ωράριο: %s" % CONTACT["hours"])
    for section in SECTIONS:
        out += ["", "## %s" % meta_text(section["title"]), ""]
        for page in section["pages"]:
            out.append("- [%s](%s/%s/%s.html): %s"
                       % (meta_text(page["title"]), SITE["url"], section["slug"],
                          page["slug"], meta_text(page["lead"])))
    out += ["", "## Επικοινωνία", "",
            "- [Επικοινωνία και ραντεβού](%s/epikoinonia.html)" % SITE["url"]]
    write("llms.txt", "\n".join(out) + "\n")


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
    build_llms()
    print("Παρήχθησαν %d σελίδες + sitemap.xml + robots.txt" % len(paths))
    for p in paths:
        print("  " + p)


if __name__ == "__main__":
    main()

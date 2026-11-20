# Elite Physiotherapy by Tatiana Gkouwir — website

Στατικό website (HTML/CSS/JS, χωρίς build dependencies) για το **Elite Physiotherapy
by Tatiana Gkouwir** — Κέντρο Φυσικοθεραπείας και Αποκατάστασης.

Ίδια αρχιτεκτονική, layout και SEO δομή με το `gynaicologos-website`
(Ρώτας Μιχάλης): sticky header με mega-menu, hero + marquee strip, reveal-on-scroll,
hub/leaf σελίδες με breadcrumbs και sticky aside, CTA band, footer 4 στηλών,
JSON-LD, canonical/OG tags, sitemap και robots.

## Δομή

```
index.html                 Αρχική
epikoinonia.html           Επικοινωνία
fysikotherapeftria/        Η Φυσικοθεραπεύτρια — βιογραφικό, μετεκπαιδεύσεις, προσέγγιση   (4 σελίδες)
ypiresies/                 Υπηρεσίες — τι αντιμετωπίζουμε                                  (7 σελίδες)
therapeies/                Θεραπείες & Τεχνικές — μέθοδοι και μέσα                         (11 σελίδες)
styles.css  main.js  assets/  assets/photos/  sitemap.xml  robots.txt
```

Σύνολο: **24 σελίδες** (1 αρχική + 1 επικοινωνία + 3 ενότητες + 19 σελίδες περιεχομένου).

## Περιεχόμενο

Αντλήθηκε από το υλικό του φακέλου `tatiana` (βιογραφικό, μετεκπαιδευτικές σπουδές,
περιγραφές θεραπευτικών μεθόδων) και αναδομήθηκε σε σημασιολογικό HTML.

## Design

**Παλέτα:** χτισμένη πάνω στο νέο logo. Το σήμα δίνει δύο χρώματα — βαθύ navy
`#1e3a5f` (hue 212°) για τη σπονδυλική στήλη και taupe `#9c8570` (hue 28°) για τη
σιλουέτα. Όλες οι αποχρώσεις κάθονται σε αυτούς τους δύο άξονες:

| Μεταβλητή | Hex | Χρήση |
| --- | --- | --- |
| `--cream` | `#fbfaf9` | φόντο σελίδας |
| `--sand` | `#eef1f5` | εναλλασσόμενα sections |
| `--blush` | `#e3e9f0` | navy wash / highlights |
| `--navy` | `#1e3a5f` | **χρώμα logo** — accent, κουμπιά, τίτλοι σε πλάγια |
| `--navy-ink` | `#1a3352` | μικρά κείμενα, links |
| `--taupe-soft` | `#9c8570` | **δεύτερο χρώμα logo** — διακοσμητικές γραμμές, εικονίδια |
| `--taupe` | `#7e6a58` | meta κείμενα (AA) |
| `--mocha` | `#806b58` | eyebrows |
| `--cocoa` | `#16293f` | τίτλοι, φόντο footer |
| `--ink` | `#23303d` | κυρίως κείμενο |

**Τυπογραφία:** Cormorant Garamond (τίτλοι) + Jost (κείμενο) — ίδια με το reference build.

**Logo στο header:** το παραδοτέο logo είναι τετράγωνο lockup (σήμα πάνω από wordmark).
Σε ύψος 56–74px το wordmark γίνεται δυσανάγνωστο, οπότε στη μπάρα χρησιμοποιείται
μόνο το σήμα (`assets/logo-mark.png`, με διαφάνεια) μαζί με ζωντανό κείμενο.
Το πλήρες lockup (`assets/logo.jpg`) χρησιμοποιείται στο footer, στο about panel
και ως `og:image` / favicon.

## Φωτογραφίες

Επιλογή της κ. Γκουβίρ από τη φωτογράφιση (Νοέμβριος 2026), ανά κατηγορία. Ζουν στο
`assets/photos/` σε δύο μεγέθη WebP: `<όνομα>.webp` (1800px) και `<όνομα>-sm.webp` (900px).

Η αντιστοίχιση φωτογραφίας → σελίδα γίνεται στο τέλος του `_build/structure.py`:

- `PHOTOS` — ανά σελίδα, η `lead` (μεγάλη, στην αρχή) και η `gallery` (πλέγμα στο τέλος)
- `HOME_PORTRAIT`, `HOME_SPACE` — το πορτρέτο και η ενότητα «Ο χώρος μας» της αρχικής
- `PHOTO_PORTRAIT` — ποιες είναι κάθετες

Για νέα φωτογραφία (χρειάζεται `cwebp`):

```bash
sips -Z 1800 πηγή.jpg --out l.jpg && cwebp -q 78 -metadata none l.jpg -o assets/photos/ονομα.webp
sips -Z 900  πηγή.jpg --out s.jpg && cwebp -q 76 -metadata none s.jpg -o assets/photos/ονομα-sm.webp
```

Οι φωτογραφίες ανοίγουν σε μεγέθυνση με κλικ (lightbox στο `main.js`).

## SEO / GEO

Εφαρμόστηκε το playbook της Astra (Νοέμβριος 2026). Όλα παράγονται από το `build.py`:

- **Δομημένα δεδομένα.** Κάθε σελίδα έχει το ίδιο βασικό γράφημα (κέντρο `#clinic`,
  φυσικοθεραπεύτρια `#tatiana-gkouvir`, `WebSite`) και δικό της schema που δείχνει σε αυτό:
  `MedicalWebPage` με `author`/`reviewedBy`, `ProfilePage` στο βιογραφικό, `CollectionPage`
  στις ενότητες, `ContactPage`, `BreadcrumbList`, `FAQPage`.
- **Συχνές ερωτήσεις.** Το `FAQS` στο `structure.py` τροφοδοτεί και το ορατό κείμενο και το
  `FAQPage`. Οι απαντήσεις λένε μόνο ό,τι γράφει ήδη η σελίδα.
- **Meta.** Περιγραφές κομμένες στους 158 χαρακτήρες, `og:image` ανά σελίδα, sitemap με
  εικόνες, `llms.txt`, γραμματοσειρές που δεν μπλοκάρουν, `?v=` στα CSS/JS.
- **`vercel.json`.** `noindex` στο `*.vercel.app` (ώστε να ευρετηριαστεί μόνο το τελικό domain)
  και cache στα assets.

**Τοπικό SEO — εκκρεμεί.** Μόλις δοθούν διεύθυνση και τηλέφωνο, συμπληρώνονται στο `CONTACT`
τα `street`, `locality`, `postal`, `region`, `lat`, `lng`, `maps_url` και το `locality_in`
(π.χ. «στη Γλυφάδα»). Το `locality_in` μπαίνει αυτόματα στους τίτλους και στο h1 της αρχικής·
τα υπόλοιπα στο schema, στα `geo.*` meta και στο `llms.txt`.

Έλεγχος: `python3 ~/.claude/skills/seo-geo-playbook/scripts/seo_audit.py .` → 0 σφάλματα.

## Ξαναχτίσιμο

```bash
python _build/build.py
```

- `_build/structure.py` — **όλο το περιεχόμενο και η δομή** (ενότητες, σελίδες,
  κείμενα, στοιχεία επικοινωνίας, μενού)
- `_build/build.py` — ο generator

Ο φάκελος `_build/` **δεν** χρειάζεται να ανέβει στον server.

## Εκκρεμότητες πριν το go-live

Οι παρακάτω τιμές είναι placeholders στο `_build/structure.py` (`CONTACT` dict).
Μόλις δοθούν, συμπληρώνονται **σε ένα σημείο** και ο generator ενημερώνει αυτόματα
τα CTA, το footer, το JSON-LD και τη σελίδα επικοινωνίας:

| Στοιχείο | Κατάσταση |
| --- | --- |
| Τηλέφωνο | Προς συμπλήρωση — όσο λείπει, όλα τα CTA δείχνουν στην `epikoinonia.html` αντί για `tel:` |
| Email | Προς συμπλήρωση |
| Διεύθυνση / Τ.Κ. / περιοχή | Προς συμπλήρωση |
| Google Maps embed | Προς συμπλήρωση — μέχρι τότε εμφανίζεται σημείωση αντί για χάρτη |
| Ωράριο | Καταχωρήθηκε γενικό («κατόπιν ραντεβού») — χρειάζεται επιβεβαίωση |
| Social links | Κενά |

Επίσης:

- **Domain.** Το `SITE["url"]` είναι `https://elitephysiotherapy.gr` (placeholder).
  Επηρεάζει canonical, OG tags, JSON-LD και sitemap — αλλάξτε το πριν το deploy.
- **Local SEO.** Δεν υπάρχει πουθενά πόλη/περιοχή στα titles και τα keywords, γιατί
  δεν είναι γνωστή η έδρα. Μόλις οριστικοποιηθεί, προστίθεται στο `HOME_META` και
  στο `CONTACT` — είναι ο μεγαλύτερος μοχλός για τοπικές αναζητήσεις.
- **Εξοπλισμός.** Οι σελίδες `therapeies/tecar-therapy.html`, `therapeies/shockwave.html`
  και `therapeies/kinesiotaping.html` περιγράφουν θεραπείες που απαιτούν μηχανήματα.
  Το υλικό αντλήθηκε από τον φάκελο — **επιβεβαιώστε ότι όντως παρέχονται στο Elite**
  πριν το go-live, αλλιώς αφαιρέστε τις από το `SECTIONS`.
- **Κείμενα νέων θεραπειών.** Οι σελίδες `diamagnitiki-antlia`, `ilektrotherapeia` και
  `presotherapeia` προστέθηκαν τον Νοέμβριο 2026 για να φιλοξενήσουν τις φωτογραφίες
  των αντίστοιχων θεραπειών. Τα κείμενά τους **δεν προέρχονται από το υλικό της
  κ. Γκουβίρ** — χρειάζονται έγκριση ή διόρθωση από την ίδια.
- **Παλιά assets.** Η προηγούμενη (χρυσή) εκδοχή του site μετακινήθηκε στο `_old/`.
  Διαγράψτε τον φάκελο όταν επιβεβαιωθεί ότι δεν χρειάζεται τίποτα από εκεί.

#!/usr/bin/env python3
"""Static site generator for NYE in Bali.

Edit data/events.json (and the CONFIG block below), then run:
    python3 build.py
The complete site is written to ./docs, which Vercel serves as-is (see vercel.json).

Prices: each listing's `price_text` shows the venue's published price in IDR. `price_from` is an
approximate AUD figure (about IDR 12,500 = $1 AUD) so the budget filter and sorting work.
"""
import json
import re
import shutil
from datetime import date
from html import escape
from pathlib import Path

# --------------------------------------------------------------------------------------
# CONFIG: change these before going live
# --------------------------------------------------------------------------------------
CONFIG = {
    "site_name": "NYE in Bali",
    "site_url": "https://nyeinbali.com",   # your live domain, no trailing slash
    "contact_email": "aj@metatapdigital.com",
    "listing_price": 599,                              # AUD
    # Listing submissions are emailed to contact_email via FormSubmit (no account needed;
    # the first submission sends a one-time activation email to that inbox).
    "form_endpoint": "https://formsubmit.co/ajax/aj@metatapdigital.com",
    # Stripe Payment Link (or similar) for the $599 listing fee. While it still contains
    # "YOUR_", submitters see a thank-you message and you email them an invoice instead.
    "payment_link": "https://buy.stripe.com/YOUR_PAYMENT_LINK",
    "year": 2026,
    "next_year": 2027,
    "idr_per_aud": 12500,                              # rough rate used for the AUD estimates
}

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
EVENTS = json.loads((ROOT / "data" / "events.json").read_text())
TODAY = date.today().isoformat()
Y, NY = CONFIG["year"], CONFIG["next_year"]
URL = CONFIG["site_url"]
RATE = f"{CONFIG['idr_per_aud']:,}"

CATEGORY_LABELS = {
    "party": "Parties",
    "beach-club": "Beach clubs",
    "dining": "Dinners",
    "fine-dining": "Fine dining",
    "gala": "Resort galas",
    "clifftop": "Clifftop",
    "rooftop": "Rooftops",
    "family": "Family-friendly",
    "budget": "Under $150 AUD",
    "free": "Free entry",
}
AREAS = sorted({e["area"] for e in EVENTS})

NAV = [
    ("/", "Home"),
    ("/#directory", "All events"),
    ("/new-years-eve-parties-bali/", "Parties"),
    ("/bali-beach-clubs-new-years-eve/", "Beach clubs"),
    ("/new-years-eve-dinner-bali/", "Dinners"),
    ("/bali-fireworks-new-years-eve/", "Fireworks"),
    ("/plan-your-night/", "Plan"),
]


def j(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")


def money(n):
    """Approximate AUD price for display (the IDR price is in price_text)."""
    return "Free" if n == 0 else f"${n:,.0f}"


def idr_from(text):
    """First IDR amount in a price_text, for schema.org offers."""
    m = re.search(r"IDR\s*([\d,]+)", text or "")
    return int(m.group(1).replace(",", "")) if m else None


# Bali silhouette: volcano, palms, a meru shrine and a split temple gate over the sea
def _palm(x, h, lean):
    tx, ty = x + lean, 200 - h
    trunk = f'<path d="M{x - 4} 200 Q{x + lean * 0.2} {200 - h * 0.55} {tx - 2} {ty} L{tx + 2} {ty} Q{x + lean * 0.25 + 5} {200 - h * 0.55} {x + 4} 200Z"/>'
    fronds = "".join(
        f'<path d="M{tx} {ty} q{dx * 0.5} {dy - 14} {dx} {dy}" fill="none" stroke="#0c0a26" stroke-width="5" stroke-linecap="round"/>'
        for dx, dy in [(-46, 14), (-34, 26), (-18, 30), (44, 12), (32, 26), (16, 32), (-6, -22), (14, -18)]
    )
    return trunk + fronds


def _meru(x, base_w, tiers):
    out, y, w = [], 186, base_w
    out.append(f'<rect x="{x - base_w / 2 - 6}" y="186" width="{base_w + 12}" height="14"/>')
    for _ in range(tiers):
        out.append(f'<path d="M{x - w / 2} {y} L{x - w / 2 + 8} {y - 14} L{x + w / 2 - 8} {y - 14} L{x + w / 2} {y}Z"/>')
        out.append(f'<rect x="{x - w / 4}" y="{y - 22}" width="{w / 2}" height="8"/>')
        y -= 22
        w *= 0.8
    out.append(f'<rect x="{x - 1.5}" y="{y - 14}" width="3" height="14"/>')
    return "".join(out)


def _gate(x):
    steps = [(0, 200, 30), (4, 176, 22), (8, 154, 14), (11, 136, 8)]
    left = "".join(f'<rect x="{x - 8 - w - o}" y="{t}" width="{w}" height="{200 - t}"/>' for o, t, w in steps)
    right = "".join(f'<rect x="{x + 8 + o}" y="{t}" width="{w}" height="{200 - t}"/>' for o, t, w in steps)
    return left + right


SKYLINE = f"""<svg class="skyline" viewBox="0 0 1440 230" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0a26"/><stop offset="1" stop-color="#07061a"/></linearGradient>
<linearGradient id="wt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1450" stop-opacity=".9"/><stop offset="1" stop-color="#07061a"/></linearGradient></defs>
<path d="M820 200 L1010 92 Q1030 82 1050 92 L1260 200Z" fill="#100d33"/>
<path d="M0 200 Q160 150 340 176 Q520 196 700 170 Q880 146 1060 176 Q1260 200 1440 168 L1440 200Z" fill="#0e0b2e"/>
<g fill="url(#sk)">
{_palm(60, 150, 26)}{_palm(118, 120, -20)}{_palm(196, 170, 34)}
{_meru(330, 80, 5)}{_gate(470)}
{_palm(560, 140, -28)}{_palm(640, 112, 20)}
{_meru(760, 64, 3)}
{_palm(900, 160, 30)}{_palm(980, 126, -24)}
{_gate(1120)}{_meru(1240, 90, 7)}
{_palm(1340, 150, -30)}{_palm(1410, 118, 22)}
<rect x="0" y="194" width="1440" height="8"/>
</g>
<rect x="0" y="198" width="1440" height="32" fill="url(#wt)"/>
</svg>"""


def countdown(mini=False):
    units = [("d", "Days"), ("h", "Hours"), ("m", "Minutes"), ("s", "Seconds")]
    inner = "".join(
        f'<div class="cd-unit"><div class="cd-num" data-u="{k}">--</div><div class="cd-label">{v}</div></div>'
        for k, v in units
    )
    return f'<div class="countdown{" mini" if mini else ""}" data-countdown role="timer" aria-label="Countdown to midnight, New Year\'s Eve {Y} in Bali (WITA)">{inner}</div>'


def layout(path, title, description, body, schema=None, og_type="website", active=None):
    canonical = URL + path
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": CONFIG["site_name"],
            "url": URL + "/",
            "potentialAction": {
                "@type": "SearchAction",
                "target": URL + "/?q={search_term_string}#directory",
                "query-input": "required name=search_term_string",
            },
        }
    ] if path == "/" else []
    schemas += schema or []
    cur = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{h}"{cur if h == (active or path) else ""}>{t}</a></li>' for h, t in NAV
    )
    ld = "".join(f'<script type="application/ld+json">{j(s)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="geo.region" content="ID-BA"><meta name="geo.placename" content="Bali">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{CONFIG['site_name']}">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{URL}/og.png"><meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{URL}/og.png">
<meta name="theme-color" content="#07061a">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap">
<a class="logo" href="/">NYE <span>in Bali</span></a>
<nav aria-label="Main"><ul>{nav}</ul></nav>
<a class="btn btn-primary btn-sm" href="/list-your-event/">List your event</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="fgrid">
<div><a class="logo" href="/">NYE <span>in Bali</span></a>
<p class="muted">The independent guide to New Year's Eve {Y} in Bali: beach club parties, clifftop clubs, resort galas, dinners and where to watch the fireworks, all in one place.</p>
{countdown(mini=True)}</div>
<div><h4>Explore</h4><ul>
<li><a href="/#directory">All NYE events</a></li><li><a href="/new-years-eve-parties-bali/">NYE parties</a></li>
<li><a href="/bali-beach-clubs-new-years-eve/">Beach clubs</a></li><li><a href="/new-years-eve-dinner-bali/">NYE dinners</a></li>
<li><a href="/family-new-years-eve-bali/">Family NYE</a></li></ul></div>
<div><h4>Plan</h4><ul>
<li><a href="/bali-fireworks-new-years-eve/">Where to watch fireworks</a></li><li><a href="/plan-your-night/">Plan your night</a></li>
<li><a href="/plan-your-night/#transport">Traffic &amp; transport</a></li><li><a href="/#faq">FAQ</a></li></ul></div>
<div><h4>Venues</h4><ul>
<li><a href="/list-your-event/">List your event: ${CONFIG['listing_price']} AUD</a></li>
<li><a href="mailto:{CONFIG['contact_email']}">{CONFIG['contact_email']}</a></li></ul></div>
</div>
<p class="fine">NYE in Bali is an independent guide and is not affiliated with any venue, the Bali Provincial Government or the Indonesian tourism authorities. Prices are shown in IDR as published by venues; AUD figures are approximate (about IDR {RATE} = $1 AUD) and "++" means tax and service (usually 21%) are added. Details can change, so always confirm with the venue before booking. Bali is a living Hindu culture: please dress and behave respectfully around temples and ceremonies. © {Y} {CONFIG['site_name']}.</p>
</div></footer>
<script src="/main.js" defer></script>
</body>
</html>"""


# --------------------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------------------
def card(e, i):
    cats = " ".join(e["categories"])
    search = " ".join([e["name"], e["venue"], e["suburb"], e["area"], " ".join(e["categories"]), e["blurb"]]).lower()
    tags = "".join(f'<span class="tag">{CATEGORY_LABELS.get(c, c)}</span>' for c in e["categories"][:3])
    price = e["price_from"]
    price_html = (
        "Free<small>entry, see details</small>" if price == 0
        else f"{money(price)}<small>from, approx AUD pp</small>" if price
        else "TBA<small>see venue</small>"
    )
    return f"""<article class="card{' featured' if e.get('featured') else ''}" data-cats="{cats}" data-area="{escape(e['area'])}" data-price="{price if price is not None else ''}" data-featured="{1 if e.get('featured') else 0}" data-order="{i}" data-search="{escape(search)}">
{'<span class="badge">Featured</span>' if e.get('featured') else ''}
<div class="loc">📍 {escape(e['suburb'] if e['suburb'] in e['area'] else e['suburb'] + ' · ' + e['area'])}</div>
<h3><a href="/events/{e['slug']}/">{escape(e['name'])}</a></h3>
<p>{escape(e['blurb'])}</p>
<div class="tags"><span class="tag fw">🎆 {escape(e['fireworks'])}</span>{tags}</div>
<div class="meta"><div class="price">{price_html}</div>
<div class="actions"><a class="btn btn-ghost btn-sm" href="/events/{e['slug']}/">Details</a><a class="btn btn-primary btn-sm" href="{e['url']}" target="_blank" rel="noopener sponsored">Book</a></div></div>
</article>"""


def directory(events, heading, sub, show_filters=True, anchor="directory"):
    used = []
    for e in events:
        for c in e["categories"]:
            if c not in used:
                used.append(c)
    order = [c for c in CATEGORY_LABELS if c in used]
    chips = '<button class="chip" data-cat="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-cat="{c}" aria-pressed="false">{CATEGORY_LABELS[c]}</button>' for c in order
    )
    areas = '<option value="all">All areas</option>' + "".join(
        f'<option>{escape(a)}</option>' for a in AREAS if any(e["area"] == a for e in events)
    )
    filters = f"""<div class="filters" role="group" aria-label="Filter by type">{chips}</div>
<div class="toolbar"><input id="q" type="search" placeholder="Search venue, area, vibe…" aria-label="Search events">
<select id="area" aria-label="Filter by area">{areas}</select>
<select id="sort" aria-label="Sort"><option value="featured">Sort: Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option></select></div>
<p class="count" aria-live="polite"></p>""" if show_filters else ""
    cards = "".join(card(e, i) for i, e in enumerate(events))
    return f"""<section id="{anchor}" data-directory><div class="wrap">
<div class="section-head"><h2>{heading}</h2><p>{sub}</p></div>
{filters}
<div class="grid">{cards}</div>
<p class="empty">No events match that search. Try another filter, or <a href="/list-your-event/">list yours</a>.</p>
</div></section>"""


def season_section(p):
    months = [
        ("October", "Planning begins",
         "Australians and international travellers book flights and villas, and start searching \"New Year's Eve Bali\". The big beach clubs release early-bird tickets and groups start comparing options.",
         "List now and you're live for the whole season, from day one."),
        ("November", "Comparing &amp; booking",
         "Travellers compare beach club tickets, resort galas and clifftop dinners side by side. Early-bird deadlines hit and premium daybeds and tables sell out.",
         "Your page, with its price, inclusions and a Book button, wins the comparison."),
        ("December", "Peak searches &amp; last-minute rush",
         "Search interest peaks as visitors land on the island and look for something to do on the night. Last tickets, late tables and walk-in countdowns get booked right up to 31 December.",
         "Sell your remaining tickets and tables while demand is at its highest."),
    ]
    cards = "".join(
        f'''<div class="card season-card"><span class="season-step">{i + 1}</span><div class="loc">{m}</div><h3>{t}</h3><p>{d}</p>
<p class="season-win">✦ {w}</p></div>''' for i, (m, t, d, w) in enumerate(months)
    )
    return f"""<section id="season"><div class="wrap">
<div class="section-head"><span class="eyebrow">The NYE search season</span>
<h2>Bali's NYE crowd books in <span class="grad">three months</span></h2>
<p>Every year, searches like "New Year's Eve Bali", "Bali NYE parties" and "NYE dinner Bali" climb from October and peak in the final weeks of December. That's when travellers choose a venue and buy tickets. If your event isn't in front of them then, they book somewhere else.</p></div>
<div class="season-bar" aria-hidden="true"><span style="--h:34%">Oct</span><span style="--h:62%">Nov</span><span style="--h:100%">Dec</span></div>
<p class="muted" style="text-align:center;font-size:.8rem;margin:-6px 0 30px">Shows the typical seasonal pattern of search interest, not exact volumes.</p>
<div class="grid">{cards}</div>
<div class="band" style="margin-top:40px">
<div><h2>One listing. The whole season.</h2><p>At typical Bali NYE prices of IDR 1.5–5 million (about $120–$400 AUD) a head, a handful of bookings covers your ${p} listing. Everything after that is profit, with zero commission.</p></div>
<a class="btn" href="#form">Claim your spot →</a></div>
</div></section>"""


def list_band():
    return f"""<section><div class="wrap"><div class="band">
<div><h2>Selling NYE tickets in Bali?</h2><p>October to December is when travellers plan New Year's Eve in Bali. Get your party, dinner or beach club in front of them for ${CONFIG['listing_price']} AUD flat, with no commission.</p></div>
<a class="btn" href="/list-your-event/">List your event →</a></div></div></section>"""


def item_list(events, name):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(events),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{URL}/events/{e['slug']}/", "name": e["name"]}
            for i, e in enumerate(events)
        ],
    }


def breadcrumbs(*pairs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + p} for i, (n, p) in enumerate(pairs)
        ],
    }


# --------------------------------------------------------------------------------------
# Content: FAQ, timeline, fireworks spots
# --------------------------------------------------------------------------------------
FAQ = [
    (f"What are the best New Year's Eve parties in Bali for {Y}?",
     f"The biggest NYE {Y} parties are the two-day FINNS NYE Festival at Berawa (Major Lazer Soundsystem, CYRIL and The Temper Trap announced), Atlas Beach Club with Quavo, and Savaya in Uluwatu with Carl Cox playing into sunrise. For something cheaper, try White Rock at Melasti, Ulu Cliffhouse, Single Fin or Motel Mexicola. See all <a href=\"/new-years-eve-parties-bali/\">Bali NYE parties</a>."),
    ("Are there fireworks in Bali on New Year's Eve?",
     "Yes, lots, but there is no single official island-wide show. At midnight, beach clubs, resorts and thousands of people on the beaches let off fireworks all along the coast from Canggu to Kuta, Jimbaran, Nusa Dua and Sanur. Kuta, Legian, Seminyak and Jimbaran beaches have some of the busiest skies. See <a href=\"/bali-fireworks-new-years-eve/\">where to watch fireworks in Bali</a>."),
    ("What time is midnight in Bali compared to Australia?",
     f"Bali is on WITA (UTC+8) with no daylight saving. Midnight in Bali on 31 December {Y} is 3am on 1 January {NY} in Sydney, Melbourne and Canberra (AEDT), 2am in Brisbane, 2:30am in Adelaide and the same time as Perth."),
    ("How much does New Year's Eve in Bali cost?",
     f"A beach-club or clifftop party ticket runs from about IDR 200,000 to IDR 5,000,000 (about $15–$400 AUD). Resort gala dinners are typically IDR 1.5–5 million per person, and top fine dining reaches IDR 8–10 million (about $640–$800 AUD). Prices marked \"++\" add about 21% tax and service. AUD figures on this site use roughly IDR {RATE} = $1 AUD."),
    ("How bad is the traffic in Bali on New Year's Eve?",
     "Very bad. Canggu, Berawa, Seminyak, Kuta, Legian and the roads to Uluwatu and Jimbaran can gridlock from late afternoon until well after midnight, and a 20-minute trip can take two hours. Pick one area, stay within walking distance of your event and pre-book a driver for any trip you can't walk."),
    ("Can I get a Grab or Gojek on New Year's Eve in Bali?",
     "Sometimes, but expect long waits, surge pricing and cancellations, especially around midnight. Some areas restrict app-based pickups, so drivers may ask you to walk to a pickup point. Pre-booking a private driver or your hotel's transfer is far more reliable."),
    ("Is it safe to drink in Bali on New Year's Eve?",
     "Stick to reputable venues and sealed, branded drinks. Australia's Smartraveller warns that methanol poisoning from spirits and cocktails has caused deaths in Indonesia, and as little as one shot can be fatal. Avoid cheap spirits and buckets, watch your drink and get urgent medical help if anyone shows symptoms such as vision problems, vomiting or confusion."),
    ("What are the best family-friendly NYE options in Bali?",
     "Nusa Dua, Sanur and Jimbaran resorts are the easiest with kids: buffets with kids' pricing at Courtyard, Westin, Hyatt Regency, Andaz and AYANA, a beach party with a magician at Karma Beach, and kids eating free at Holiday Inn Canggu. See <a href=\"/family-new-years-eve-bali/\">family NYE in Bali</a>."),
    ("Is Nyepi on New Year's Eve?",
     f"No. Nyepi, the Balinese Day of Silence, is the Balinese Saka new year and falls in March, when the whole island (including the airport) shuts down for 24 hours. New Year's Eve on 31 December is a normal party night in Bali, and Nyepi does not affect it."),
    ("Do I need a visa or pay a tourist levy for Bali?",
     "Australians and many other nationalities can get a visa on arrival (IDR 500,000), ideally as an e-VOA online before you fly via the official Indonesian immigration site. Every international visitor must also pay the IDR 150,000 Bali tourist levy, through the official Love Bali website or app, and complete the All Indonesia arrival card. Check current rules on official government sites before you travel."),
    ("Is NYE in Bali an official Bali Government website?",
     "No. NYE in Bali is an independent guide and event directory. We bring together published NYE events from beach clubs, resorts and restaurants so you can compare and plan the whole night in one place."),
    ("How do I list my New Year's Eve event on NYE in Bali?",
     f"It's a one-off ${CONFIG['listing_price']} AUD fee with no commission. Your event gets its own optimised page, a place in our directory and category pages, and a direct link to your booking page. <a href=\"/list-your-event/\">List your event here</a>."),
]


def faq_html(items):
    return "".join(f"<details><summary>{escape(q)}</summary><p>{a}</p></details>" for q, a in items)


def faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }


TIMELINE = [
    ("From 1pm", "The big beach clubs open their gates (Atlas from 1pm, FINNS from 2pm). Arrive early: queues and traffic build fast."),
    ("Mid-afternoon", "Traffic starts to snarl in Canggu, Seminyak, Kuta and on the Bukit. Get where you're going and stay there."),
    ("Around 6:30pm", "The last sunset of the year. Clifftop bars in Uluwatu and beaches on the west coast are the places to see it."),
    ("7pm – 8pm", "Resort gala dinners and NYE set menus begin. Many have early and late options."),
    ("From 10pm", "Countdown parties start at hotels and bars. Beaches fill with locals and visitors."),
    ("Midnight (WITA)", f"Fireworks erupt along the whole coastline to welcome {NY}. It's 3am in Sydney and Melbourne."),
    ("After midnight", "Roads stay gridlocked for hours and ride apps surge. Stay put, or walk to a pre-booked pickup point."),
    ("Sunrise", "The die-hards finish at Savaya, where Carl Cox plays the first sunrise of the year."),
]


def timeline_html():
    return '<div class="timeline">' + "".join(
        f'<div class="tl"><b>{t}</b><p>{d}</p></div>' for t, d in TIMELINE
    ) + "</div>"


VANTAGE = [
    ("Kuta Beach", "Kuta", "Huge crowd, displays all along the bay", "free", "Busiest beach on the island. Watch your bags and stand back from amateur fireworks"),
    ("Legian & Double Six Beach", "Legian", "Long beach, hotel and bar displays", "free", "Beach bars along the sand; a little calmer than Kuta"),
    ("Seminyak & Petitenget Beach", "Seminyak", "Beach club and resort fireworks", "free", "The beach clubs are ticketed but the sand in front is public"),
    ("Berawa Beach", "Canggu", "Next to the FINNS and Atlas shows", "free", "Roads gridlock early; walk in from nearby stays"),
    ("Batu Bolong & Echo Beach", "Canggu", "Beach bars and clubs", "free", "Lively and young; scooters everywhere, so take care"),
    ("Jimbaran Bay", "Jimbaran", "Displays right around the bay", "check", "Book a table at a seafood café on the sand for the best spot"),
    ("Rock Bar, AYANA", "Jimbaran", "Cliffside over the bay", "paid", "Minimum spend on NYE; queues are long"),
    ("Sanur Beach path", "Sanur", "Hotel displays along the beachwalk", "free", "Calm and family-friendly; easy to walk between hotels"),
    ("Nusa Dua beaches", "Nusa Dua", "Resort fireworks along the coast", "check", "Mostly resort beachfronts; use public access points such as Geger"),
    ("Melasti Beach", "Ungasan", "Beach under limestone cliffs", "check", "Access rules can change; beach clubs here are ticketed"),
    ("Uluwatu clifftop bars", "Uluwatu", "Sunset and distant coastal displays", "free-t", "Some bars, like Single Fin, have had free entry early in the evening"),
    ("Ubud", "Ubud", "Few fireworks, village celebrations", "check", "Best for a quiet dinner; little coastal fireworks view"),
]
PILL = {
    "free": '<span class="pill free">Free</span>',
    "free-t": '<span class="pill free">Free early</span>',
    "paid": '<span class="pill paid">Paid / min spend</span>',
    "check": '<span class="pill af">Check access</span>',
}


def vantage_table(rows=None):
    rows = rows or VANTAGE
    body = "".join(
        f"<tr><td><b>{n}</b></td><td>{a}</td><td>{v}</td><td>{PILL[t]}</td><td class='muted'>{note}</td></tr>"
        for n, a, v, t, note in rows
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Where to watch</th><th>Area</th><th>View</th><th>Entry</th><th>Good to know</th></tr></thead>
<tbody>{body}</tbody></table></div>"""


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
DIR_SUB = 'Filter by type, area or budget. Prices are shown in IDR as published, with approximate AUD. "++" means tax and service (about 21%) are added.'


def page_home():
    featured = [e for e in EVENTS if e.get("featured")]
    rest = [e for e in EVENTS if not e.get("featured")]
    ordered = featured + rest
    n = len(EVENTS)
    body = f"""
<section class="hero"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap">
<span class="eyebrow">Thursday 31 December {Y} · Bali, Indonesia</span>
<h1>New Year's Eve in Bali {Y}<br><span class="grad">parties, beach clubs &amp; dinners</span></h1>
<p class="lead">The best NYE events in Bali in one place: beach club parties in Canggu and Seminyak, clifftop clubs in Uluwatu, resort galas, dinners with fireworks and where to watch for free. Compare, choose and book your night to welcome {NY}.</p>
{countdown()}
<p class="cd-note">until midnight in Bali (WITA, UTC+8)</p>
<div class="cta-row"><a class="btn btn-primary" href="#directory">Browse {n}+ NYE events</a><a class="btn btn-ghost" href="/bali-fireworks-new-years-eve/">Where to watch fireworks</a></div>
</div></section>

<div class="wrap"><div class="facts">
<div class="fact"><b>Midnight</b><span>WITA (UTC+8), which is 3am in Sydney &amp; Melbourne</span></div>
<div class="fact"><b>Coast-wide</b><span>fireworks from beaches, clubs and resorts, with no single official show</span></div>
<div class="fact"><b>~IDR {RATE}</b><span>to $1 AUD, the rate our AUD estimates use</span></div>
<div class="fact"><b>{n}+</b><span>bookable parties, beach clubs, dinners &amp; galas</span></div>
</div></div>

{directory(ordered, f"Every Bali NYE {Y} event in one directory", DIR_SUB)}

{list_band()}

<section class="alt"><div class="wrap two">
<div><h2>Your NYE {Y} in Bali, <span class="grad">hour by hour</span></h2>
<p class="muted">Timings are based on recent years and published 2026 events. Use this to plan when to arrive, eat and move, and above all to beat the traffic.</p>
<a class="btn btn-ghost" href="/plan-your-night/">Full planning guide →</a></div>
{timeline_html()}
</div></section>

<section><div class="wrap">
<div class="section-head"><h2>Where to watch the fireworks</h2><p>Bali has no single official fireworks show. Instead, the sky lights up along the whole coast at midnight. These are the best free and paid spots.</p></div>
{vantage_table(VANTAGE[:8])}
<p style="text-align:center;margin-top:24px"><a class="btn btn-ghost" href="/bali-fireworks-new-years-eve/">See all fireworks spots →</a></p>
</div></section>

<section class="alt"><div class="wrap">
<div class="section-head"><h2>Find your kind of NYE</h2></div>
<div class="grid">
<div class="card"><h3><a href="/new-years-eve-parties-bali/">🎉 NYE parties in Bali</a></h3><p>FINNS, Atlas, Savaya, Potato Head and clifftop parties from free entry to IDR 5 million.</p><a href="/new-years-eve-parties-bali/">Browse parties →</a></div>
<div class="card"><h3><a href="/bali-beach-clubs-new-years-eve/">🏝️ Beach clubs on NYE</a></h3><p>Canggu, Seminyak and Uluwatu beach clubs with DJs, pools and midnight fireworks.</p><a href="/bali-beach-clubs-new-years-eve/">Browse beach clubs →</a></div>
<div class="card"><h3><a href="/new-years-eve-dinner-bali/">🍽️ NYE dinners &amp; resort galas</a></h3><p>From IDR 455,000 family buffets to clifftop degustations at Bvlgari and Raffles.</p><a href="/new-years-eve-dinner-bali/">Browse dinners →</a></div>
<div class="card"><h3><a href="/family-new-years-eve-bali/">👨‍👩‍👧 Family-friendly NYE</a></h3><p>Resort buffets with kids' pricing, beach parties and early countdowns.</p><a href="/family-new-years-eve-bali/">Browse family events →</a></div>
</div></div></section>

<section id="faq"><div class="wrap">
<div class="section-head"><h2>New Year's Eve in Bali {Y}: FAQ</h2></div>
<div class="faq">{faq_html(FAQ)}</div>
</div></section>
"""
    return layout(
        "/",
        f"New Year's Eve in Bali {Y}: NYE Parties, Beach Clubs & Dinners | NYE in Bali",
        f"Plan New Year's Eve {Y} in Bali: live countdown, {n}+ NYE parties, beach clubs, resort galas and dinners in Canggu, Seminyak, Uluwatu and beyond, plus fireworks spots and traffic tips.",
        body,
        schema=[item_list(ordered, f"New Year's Eve {Y} events in Bali"), faq_schema(FAQ),
                {"@context": "https://schema.org", "@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/",
                 "logo": URL + "/favicon.svg", "email": CONFIG["contact_email"]}],
    )


CATEGORY_PAGES = [
    {
        "path": "/new-years-eve-parties-bali/",
        "filter": lambda e: "party" in e["categories"],
        "title": f"Bali NYE Parties {Y}: Best New Year's Eve Parties in Bali",
        "h1": f"The best New Year's Eve parties in Bali {Y}",
        "desc": f"Bali's best New Year's Eve parties for {Y}: FINNS NYE Festival, Atlas with Quavo, Savaya with Carl Cox, plus Seminyak, Canggu and Uluwatu parties with prices in IDR and AUD.",
        "intro": "From two-day beach festivals in Berawa to sunrise sets on the Uluwatu cliffs, these are the best NYE parties in Bali. Big-name events sell out months ahead, while plenty of bars and clifftop clubs keep entry cheap or free early in the evening.",
        "tips": ["Buy the big tickets (FINNS, Atlas, Savaya) early. Releases go up in price and sell out.", "Check the age rules: Savaya is strictly 21+, FINNS 18+ and Atlas 16+.", "Pick a party near where you're staying. NYE traffic makes hopping between areas almost impossible.", "Drink only sealed, branded drinks at reputable venues because of methanol risk."],
    },
    {
        "path": "/bali-beach-clubs-new-years-eve/",
        "filter": lambda e: "beach-club" in e["categories"],
        "title": f"Bali Beach Clubs on New Year's Eve {Y}: NYE Tickets & Prices",
        "h1": f"Bali beach clubs on New Year's Eve {Y}",
        "desc": f"Compare Bali beach club NYE {Y} parties: FINNS, Atlas, Potato Head, La Brisa, KU DE TA, Sundays, White Rock and more, with ticket prices, times and fireworks.",
        "intro": "Bali's beach clubs are the heart of its New Year's Eve. Most open in the afternoon, run DJs through sunset and finish with fireworks over the sand at midnight. Day passes, daybeds and VIP sofas all sell separately and the best spots go first.",
        "tips": ["Daybeds and sofas are usually mostly food and drink credit, so compare the true cost.", "Most big beach clubs are cashless with wristbands. Load up early to avoid queues.", "Re-entry is often not allowed on NYE, so bring what you need for the day.", "Pack sunscreen, a hat and a light rain layer: it's wet season."],
    },
    {
        "path": "/new-years-eve-dinner-bali/",
        "filter": lambda e: "dining" in e["categories"] or "fine-dining" in e["categories"] or "gala" in e["categories"],
        "title": f"New Year's Eve Dinner Bali {Y}: Resort Galas & NYE Set Menus",
        "h1": f"New Year's Eve dinners in Bali {Y}",
        "desc": f"The best New Year's Eve dinners in Bali for {Y}: resort galas in Nusa Dua and Jimbaran, clifftop degustations in Uluwatu, beachfront set menus in Seminyak and Ubud dinners, with IDR and AUD prices.",
        "intro": "A resort gala or long NYE dinner is the most comfortable way to see in the new year in Bali: no traffic once you're there, a guaranteed table and, at most beachfront and clifftop resorts, fireworks at midnight. Expect most prices to be quoted \"++\", with about 21% tax and service on top.",
        "tips": ["Book by November. The best tables and early-bird deals go first.", "Check whether the price includes drinks. Free-flow packages are often good value.", "Ask whether the venue has its own fireworks or just views of others.", "Staying at the resort? In-house guests often get priority or better rates."],
    },
    {
        "path": "/family-new-years-eve-bali/",
        "filter": lambda e: "family" in e["categories"],
        "title": f"Family New Year's Eve Bali {Y}: Kid-Friendly NYE Dinners & Countdowns",
        "h1": f"Family-friendly New Year's Eve in Bali {Y}",
        "desc": f"Kid-friendly ways to celebrate New Year's Eve {Y} in Bali: resort buffets with kids' pricing in Nusa Dua, Sanur and Jimbaran, beach parties, early dinners and fireworks.",
        "intro": "Bali is a brilliant place for a family New Year's Eve if you stay put. Nusa Dua, Sanur and Jimbaran resorts run buffets with kids' pricing, entertainers and fireworks on the beach, so you can celebrate and walk back to your room.",
        "tips": ["Choose a dinner at or near your hotel so you don't spend the night in traffic.", "Check children's pricing and age rules. Some galas exclude under-12s.", "Bring ear protection for little ones: fireworks go off all around you on the beach.", "Agree on a meeting point. Beaches get very crowded at midnight."],
    },
]


def page_category(c):
    events = [e for e in EVENTS if c["filter"](e)]
    events.sort(key=lambda e: (not e.get("featured"), e["price_from"] if e["price_from"] is not None else 1e9))
    tips = "".join(f"<li>{t}</li>" for t in c["tips"])
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Bali</span><h1>{c['h1']}</h1>
<p class="lead">{c['intro']}</p>{countdown(mini=True)}</div></section>
<section style="padding-bottom:0"><div class="wrap two">
<div class="panel"><h2 style="font-size:1.5rem">Booking tips</h2><ul class="ticks">{tips}</ul></div>
<div><h2 style="font-size:1.5rem">{len(events)} options, compared</h2><p class="muted">Every listing shows the published IDR price, an approximate AUD "from" price, what's included and whether there are fireworks. Where 2026 pricing isn't out yet we show last year's price or TBA, so always confirm with the venue.</p>
<a class="btn btn-primary" href="/list-your-event/">Add your venue: ${CONFIG['listing_price']} AUD</a></div>
</div></section>
{directory(events, c['h1'], 'Filter and sort to find your night.')}
{list_band()}"""
    return layout(
        c["path"], c["title"] + " | NYE in Bali", c["desc"], body,
        schema=[item_list(events, c["h1"]), breadcrumbs(("Home", "/"), (c["h1"], c["path"]))],
    )


def page_event(e):
    path = f"/events/{e['slug']}/"
    inc = "".join(f"<li>{escape(x)}</li>" for x in e["includes"])
    cats = ", ".join(CATEGORY_LABELS.get(c, c) for c in e["categories"])
    related = [x for x in EVENTS if x["slug"] != e["slug"] and (x["area"] == e["area"] or set(x["categories"]) & set(e["categories"]))][:3]
    offer = {"@type": "Offer", "url": e["url"], "availability": "https://schema.org/InStock", "validFrom": f"{Y}-01-01"}
    idr = idr_from(e["price_text"])
    if e["price_from"] == 0:
        offer.update(price=0, priceCurrency="IDR")
    elif idr:
        offer.update(price=idr, priceCurrency="IDR")
    elif e["price_from"] is not None:
        offer.update(price=e["price_from"], priceCurrency="AUD")
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": f"{e['name']}, New Year's Eve {Y}",
        "description": e["blurb"] + " Includes: " + "; ".join(e["includes"]) + ".",
        "startDate": f"{Y}-12-31",
        "endDate": f"{NY}-01-01",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "image": [f"{URL}/og.png"],
        "location": {
            "@type": "Place", "name": e["venue"],
            "address": {"@type": "PostalAddress", "addressLocality": e["suburb"], "addressRegion": "Bali", "addressCountry": "ID"},
        },
        "organizer": {"@type": "Organization", "name": e["venue"].split(",")[0], "url": e["url"]},
        "offers": offer,
    }
    venue_short = e["venue"].split(",")[0]
    body = f"""
<section class="event-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/#directory">NYE events</a> › {escape(e['name'])}</nav>
<span class="eyebrow">New Year's Eve {Y} · {escape(e['suburb'])}, {escape(e['area'])}</span>
<h1 style="font-size:clamp(2rem,5vw,3.4rem)">{escape(e['name'])}</h1>
<p class="lead muted" style="font-size:1.15rem;max-width:760px">{escape(e['blurb'])}</p>
</div></section>
<section style="padding-top:10px"><div class="wrap event-layout">
<div>
<div class="panel"><h2 style="font-size:1.5rem">What's included</h2><ul class="ticks">{inc}</ul></div>
<div class="prose" style="margin-top:30px">
<h2 style="font-size:1.5rem">About {escape(e['name'])}</h2>
<p>{escape(e['name'])} is at {escape(e['venue'])} in {escape(e['suburb'])} ({escape(e['area'])}). It's one of the {escape(cats.lower())} options for New Year's Eve {Y} in Bali. Fireworks: <b>{escape(e['fireworks'])}</b>. Age: <b>{escape(e['age'])}</b>.</p>
<p><b>Price:</b> {escape(e['price_text'])}. "++" means tax and service (usually 21%) are added; AUD figures are approximate.</p>
<p>Planning the rest of your night? Read our <a href="/plan-your-night/">NYE traffic, transport and safety tips</a> or see <a href="/bali-fireworks-new-years-eve/">where to watch the fireworks</a>.</p>
<p class="notice">Details are based on the venue's published NYE information (or last year's, where marked) and can change. Confirm the price, times and inclusions with {escape(venue_short)} before booking. Are you the venue? <a href="/list-your-event/">Claim and upgrade this listing</a>.</p>
</div></div>
<aside class="side panel">
<div class="price" style="font-size:2rem">{"Free" if e['price_from']==0 else money(e['price_from']) + ' <span style="font-size:1rem">AUD approx</span>' if e['price_from'] else "TBA"}<small>{escape(e['price_text'])}</small></div>
<dl><dt>Date</dt><dd>Thursday 31 December {Y}</dd><dt>Time</dt><dd>{escape(e['time'])}</dd>
<dt>Where</dt><dd>{escape(e['venue'])}</dd><dt>Fireworks</dt><dd>🎆 {escape(e['fireworks'])}</dd><dt>Age</dt><dd>{escape(e['age'])}</dd></dl>
<a class="btn btn-primary" style="width:100%;justify-content:center" href="{e['url']}" target="_blank" rel="noopener sponsored">Book with the venue →</a>
<div style="margin-top:20px">{countdown(mini=True)}</div>
</aside>
</div></section>
<section class="alt"><div class="wrap"><div class="section-head"><h2>You might also like</h2></div>
<div class="grid">{''.join(card(x, i) for i, x in enumerate(related))}</div></div></section>
{list_band()}"""
    return layout(
        path,
        (f"{e['name']} {Y}" if "NYE" in e["name"] or "New Year" in e["name"] else f"{e['name']} NYE {Y}")
        + f" – {e['suburb']}, Bali | NYE in Bali",
        f"{e['name']} New Year's Eve {Y} in {e['suburb']}, Bali: {e['price_text']}. {e['blurb']}"[:300],
        body, og_type="article", active="/#directory",
        schema=[schema, breadcrumbs(("Home", "/"), ("NYE events", "/#directory"), (e["name"], path))],
    )


def page_fireworks():
    fw = [e for e in EVENTS if "fireworks" in e["fireworks"].lower() and "tbc" not in e["fireworks"].lower()]
    fw.sort(key=lambda e: (not e.get("featured"), e["price_from"] if e["price_from"] is not None else 1e9))
    faq = [FAQ[1], FAQ[2], FAQ[4], FAQ[6]]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Free &amp; ticketed</span>
<h1>Where to watch fireworks in Bali on New Year's Eve {Y}</h1>
<p class="lead">Bali doesn't have one official fireworks show. At midnight the whole coastline lights up instead, from beach clubs, resorts and crowds on the sand. Here are the best free beaches and the venues that put on their own display.</p></div></section>
<section><div class="wrap">
<div class="section-head"><h2>Fireworks spots at a glance</h2><p>Beaches in Bali are public, but access through resorts and beach clubs is not. Arrive before 11pm, keep your distance from people setting off their own fireworks and keep valuables at your hotel.</p></div>
{vantage_table()}
</div></section>
{directory(fw, "NYE events with their own fireworks", "Book a party, dinner or beach club that puts on a midnight display, so you get a guaranteed view, a seat and a bar.", show_filters=False)}
<section class="alt"><div class="wrap prose">
<h2>How to choose where to watch</h2>
<p><b>For the biggest skies</b>, head to Kuta, Legian or Seminyak beach. Dozens of hotels, bars and families let off fireworks along a few kilometres of sand.</p>
<p><b>For a view across the water</b>, Jimbaran Bay is hard to beat. Book a seafood café on the beach and watch displays all around the curve of the bay.</p>
<p><b>For somewhere calm</b>, Sanur's beachwalk and the Nusa Dua resorts are quieter, more family-friendly and much easier to get around.</p>
<p><b>For drama</b>, the Uluwatu cliffs give you the last sunset of the year and fireworks over the Indian Ocean from clifftop venues like Ulu Cliffhouse, Renaissance and Jumeirah.</p>
<h2>What to bring</h2>
<ul><li>A light rain jacket or poncho. December is wet season and storms are common</li><li>Water and insect repellent</li><li>Charged phone, power bank and your hotel location pinned in Google Maps</li><li>A little cash in case card machines or wristband systems go down</li><li>Ear protection for children</li></ul>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Fireworks FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/bali-fireworks-new-years-eve/",
        f"Bali New Year's Eve Fireworks {Y}: Where to Watch (Free & Ticketed) | NYE in Bali",
        f"Where to watch the fireworks in Bali on New Year's Eve {Y}: free beaches in Kuta, Seminyak, Jimbaran and Sanur, clifftop spots in Uluwatu and NYE events with their own midnight display.",
        body, schema=[faq_schema(faq), item_list(fw, "Bali NYE events with fireworks"),
                      breadcrumbs(("Home", "/"), ("Fireworks", "/bali-fireworks-new-years-eve/"))],
    )


def page_plan():
    faq = [FAQ[4], FAQ[5], FAQ[6], FAQ[8], FAQ[9], FAQ[2]]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">Planning guide</span>
<h1>Plan your Bali NYE {Y}</h1>
<p class="lead">How the night runs, beating the NYE traffic, Grab and Gojek, private drivers, scooter and drink safety, and the entry rules you need before you fly.</p>
{countdown(mini=True)}</div></section>
<section><div class="wrap two" style="align-items:start">
<div><h2>How the night runs</h2><p class="muted">Based on recent years and 2026 events published so far. Bali is on WITA (UTC+8), three hours behind Sydney in summer.</p></div>
{timeline_html()}
</div></section>
<section class="alt" id="transport"><div class="wrap prose">
<h2>Traffic: the one thing that ruins NYE in Bali</h2>
<p>South Bali's roads are narrow and on New Year's Eve they jam solid. Canggu and Berawa, Seminyak, Kuta and Legian, the Bypass to Jimbaran and Nusa Dua, and the roads up to Uluwatu can gridlock from mid-afternoon until long after midnight. A 20-minute trip can take two hours or more.</p>
<ul><li><b>Pick one area</b> for the night (ideally for a few nights) and book your dinner, party and accommodation there.</li>
<li><b>Stay within walking distance</b> of your main event if you can. It's the single best decision you can make.</li>
<li><b>Don't plan to venue-hop.</b> Dinner in Seminyak and a party in Uluwatu on the same night rarely works.</li>
<li><b>Leave early.</b> Get to beach clubs in the afternoon and resorts well before your dinner time.</li></ul>
<h2 id="rides">Grab, Gojek &amp; private drivers</h2>
<p>Ride apps work in Bali, but on NYE expect long waits, surge pricing and drivers cancelling, especially from 10pm to 2am. Some areas restrict app pickups, so you may be asked to walk to a pickup point. The reliable option is a <b>pre-booked private driver</b> or your hotel's transfer: book it days ahead, agree the pickup point and time, and save the driver's WhatsApp number. Motorbike rides (GrabBike, GoRide) move faster in traffic but are risky late at night.</p>
<h2 id="scooters">Scooters</h2>
<p>NYE is the worst night of the year to ride a scooter in Bali: gridlock, rain, fireworks and lots of drunk riders. Australia's Smartraveller notes you need a valid motorcycle licence, including an International Driving Permit, to ride legally, and travel insurers often refuse claims for unlicensed riders or riding after drinking. Walk, or get a driver.</p>
<h2 id="safety">Drinks safety</h2>
<ul><li><b>Methanol:</b> Smartraveller warns of deaths from methanol poisoning in Indonesia, and as little as one shot can be fatal. Drink at reputable venues, stick to sealed, branded drinks and avoid cheap spirits, buckets and local arak from unknown sources.</li>
<li>Watch your drink and don't accept open drinks from strangers.</li>
<li>Seek urgent medical help for anyone with blurred vision, vomiting, confusion or breathing trouble after drinking.</li>
<li>Drink plenty of water. It's hot and humid, even at midnight.</li></ul>
<h2 id="entry">Before you fly: visa, levy and arrival card</h2>
<ul><li><b>Visa on arrival:</b> Australians and many other nationalities can get a 30-day visa on arrival (IDR 500,000). Apply for the e-VOA online before you fly through the official Indonesian immigration site to skip airport queues.</li>
<li><b>Bali tourist levy:</b> IDR 150,000 per international visitor, paid through the official Love Bali website or app (lovebali.baliprov.go.id). It's separate from the visa.</li>
<li><b>All Indonesia arrival card:</b> complete the free online arrival declaration shortly before you travel.</li>
<li>Beware of look-alike websites charging extra fees. Use official government sites, and check current rules before you travel as they change often.</li></ul>
<h2 id="nyepi">Don't confuse NYE with Nyepi</h2>
<p>Nyepi, the Balinese Day of Silence, marks the Balinese Saka new year and falls in March. On Nyepi the whole island, including the airport, shuts down for 24 hours. It has nothing to do with 31 December, which is a normal (and very busy) party night.</p>
<h2>Weather</h2>
<p>Late December is the wet season: hot (around 30°C by day), humid and often stormy. Pack a light rain layer, check the hourly forecast on the day and choose venues with covered areas if you're worried.</p>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Planning FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/plan-your-night/",
        f"Bali NYE {Y} Planning Guide: Traffic, Transport & Safety | NYE in Bali",
        f"Plan New Year's Eve {Y} in Bali: how the night runs, NYE traffic, Grab and Gojek, private drivers, scooter and methanol safety, visa on arrival and the IDR 150,000 tourist levy.",
        body, schema=[faq_schema(faq), breadcrumbs(("Home", "/"), ("Plan your night", "/plan-your-night/"))],
    )


def page_list():
    p = CONFIG["listing_price"]
    has_pay = "YOUR_" not in CONFIG["payment_link"]
    form_sub = (f"Fill this in, then pay ${p} AUD securely. We'll publish your page and email you the link." if has_pay
                else f"Fill this in and we'll email you a ${p} AUD invoice within one business day. Your page goes live once it's paid.")
    submit_label = f"Continue to payment: ${p} →" if has_pay else "Send my listing request →"
    cats = "".join(f'<option value="{k}">{v}</option>' for k, v in CATEGORY_LABELS.items() if k not in ("budget", "free"))
    faq = [
        ("What do I get for $" + str(p) + " AUD?", "A dedicated event page built for search, with Google Event structured data. You also get a listing in our main directory and the matching category pages (parties, beach clubs, dinners, family), a direct link to your own booking page, and edits until 31 December."),
        ("Why should I list now rather than in December?", "Search interest in New Year's Eve in Bali builds from October and peaks in the final weeks of December, as travellers book flights and then look for things to do. Listing early means your page is live and indexed by Google for the whole season, not just the last-minute rush. New pages can take days or weeks to rank, so the earlier you're in, the more of the season you capture. It's the same $" + str(p) + " whenever you list."),
        ("Can I pay in rupiah?", f"The listing fee is ${p} AUD, paid by card through a secure payment link, so it works from an Indonesian or international card. Your event's own prices can be shown in IDR."),
        ("Do you take commission on bookings?", "No. Guests book directly with you through your own link, and you keep 100% of every ticket."),
        ("How long does my listing stay live?", f"Your listing stays live until New Year's Day {NY}, then rolls into our archive. Previous listers get first right to renew for next year."),
        ("How fast will my listing go live?", "Usually within one business day of payment. We'll email you the link."),
        ("Can I update prices or details?", "Yes. Email us any changes (sold-out tiers, price releases, new DJs) and we'll update your page."),
    ]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">For beach clubs, resorts, restaurants &amp; promoters</span>
<h1>List your New Year's Eve event in Bali</h1>
<p class="lead">October, November and December are when travellers plan New Year's Eve in Bali. Put your NYE {Y} event in front of people typing "New Year's Eve Bali", "Bali NYE parties", "NYE dinner Bali" and "Canggu New Year's Eve" while they're choosing where to spend the night.</p>
{countdown(mini=True)}
<p class="cd-note" style="margin-top:0">left to sell. The NYE search season is on now.</p>
<div class="cta-row"><a class="btn btn-primary" href="#form">List my event: ${p}</a><a class="btn btn-ghost" href="#season">Why now?</a></div></div></section>
{season_section(p)}
<section><div class="wrap two" style="align-items:start">
<div>
<h2>Why list with <span class="grad">NYE in Bali</span>?</h2>
<ul class="ticks">
<li><b>High-intent visitors.</b> People only visit a NYE guide when they're about to book.</li>
<li><b>Your own SEO page.</b> Each event gets a dedicated page with Google Event schema, which can make it eligible for event rich results.</li>
<li><b>Listed where people browse.</b> You appear in the main directory plus every matching category: parties, beach clubs, dinners and family.</li>
<li><b>Zero commission.</b> Guests click straight through to your booking page.</li>
<li><b>Updates until NYE.</b> Change prices, add releases or mark sold-out tiers whenever you like.</li>
<li><b>Our name is the search.</b> NYE in Bali is built around the exact phrases travellers type into Google, so every page targets them.</li>
<li><b>Australian and international travellers.</b> Prices in IDR with AUD estimates, written for the visitors who book Bali NYE.</li>
</ul>
</div>
<div class="pricing">
<span class="eyebrow">NYE {Y} listing</span>
<div class="amount"><sup>$</sup>{p}</div>
<p class="muted">AUD · one-off · no commission</p>
<ul class="ticks">
<li>Dedicated event page + Google Event schema</li>
<li>Directory &amp; category page placement</li>
<li>Direct "Book" button to your site</li>
<li>Unlimited edits until 31 Dec {Y}</li>
<li>Live within 1 business day</li>
</ul>
<a class="btn btn-primary" href="#form" style="width:100%;justify-content:center">List my event →</a>
</div>
</div></section>
<section class="alt" id="form"><div class="wrap" style="max-width:860px">
<div class="section-head"><h2>Your event details</h2><p>{form_sub}</p></div>
<form class="listing panel" data-endpoint="{CONFIG['form_endpoint']}" data-payment="{CONFIG['payment_link']}" data-email="{CONFIG['contact_email']}">
<div><label for="f-name">Event name *</label><input id="f-name" name="event_name" required></div>
<div><label for="f-venue">Venue *</label><input id="f-venue" name="venue" required></div>
<div><label for="f-suburb">Area *</label><input id="f-suburb" name="suburb" required placeholder="e.g. Canggu, Uluwatu"></div>
<div><label for="f-cat">Type *</label><select id="f-cat" name="category" required>{cats}</select></div>
<div><label for="f-price">Price from (IDR pp)</label><input id="f-price" name="price_from" inputmode="decimal" placeholder="e.g. 1,500,000++"></div>
<div><label for="f-time">Times</label><input id="f-time" name="times" placeholder="e.g. 4pm – 2am"></div>
<div><label for="f-fw">Fireworks</label><select id="f-fw" name="fireworks"><option>Our own midnight fireworks</option><option>Views of nearby fireworks</option><option>No fireworks</option></select></div>
<div><label for="f-age">Age</label><select id="f-age" name="age"><option>18+</option><option>21+</option><option>All ages</option><option>Family-friendly</option></select></div>
<div class="full"><label for="f-url">Booking URL *</label><input id="f-url" name="booking_url" type="url" required placeholder="https://"></div>
<div class="full"><label for="f-desc">Description &amp; inclusions *</label><textarea id="f-desc" name="description" required placeholder="What makes your night special? Food, drinks, DJs, views…"></textarea></div>
<div><label for="f-contact">Contact name *</label><input id="f-contact" name="contact_name" required></div>
<div><label for="f-email">Email *</label><input id="f-email" name="email" type="email" required></div>
<div><label for="f-phone">Phone / WhatsApp</label><input id="f-phone" name="phone" type="tel"></div>
<div><label for="f-abn">Business name</label><input id="f-abn" name="business"></div>
<input type="hidden" name="_subject" value="New NYE in Bali listing request (${p} AUD)">
<input type="hidden" name="_template" value="table"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="full"><button class="btn btn-primary" type="submit">{submit_label}</button>
<p class="form-status muted" aria-live="polite" style="margin:12px 0 0"></p></div>
</form>
</div></section>
<section><div class="wrap"><div class="section-head"><h2>Listing FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>"""
    service = {
        "@context": "https://schema.org", "@type": "Service", "name": f"NYE {Y} event listing",
        "provider": {"@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/"},
        "areaServed": "Bali, Indonesia",
        "offers": {"@type": "Offer", "price": p, "priceCurrency": "AUD", "url": URL + "/list-your-event/"},
    }
    return layout(
        "/list-your-event/",
        f"List Your New Year's Eve Event in Bali – ${p} | NYE in Bali",
        f"Promote your Bali New Year's Eve {Y} party, beach club, gala or dinner. ${p} AUD flat fee, no commission: a dedicated SEO event page, directory placement and a direct booking link.",
        body, schema=[service, faq_schema(faq), breadcrumbs(("Home", "/"), ("List your event", "/list-your-event/"))],
    )


def page_404():
    body = f"""<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}<div class="wrap">
<h1>This page fizzled out</h1><p class="lead">The page you're after isn't here, but the fireworks still are.</p>{countdown()}
<div class="cta-row"><a class="btn btn-primary" href="/">Back to all NYE events</a></div></div></section>"""
    return layout("/404.html", "Page not found | NYE in Bali", "Page not found.", body).replace(
        'content="index,follow', 'content="noindex,follow')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#07061a"/><g stroke-linecap="round" stroke-width="4"><path d="M32 32 32 8" stroke="#ffc94d"/><path d="M32 32 53 20" stroke="#ff4fa3"/><path d="M32 32 53 44" stroke="#8b5cff"/><path d="M32 32 32 56" stroke="#41e3ff"/><path d="M32 32 11 44" stroke="#ffc94d"/><path d="M32 32 11 20" stroke="#ff4fa3"/></g><circle cx="32" cy="32" r="5" fill="#fff"/></svg>"""

OG_HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Playfair+Display:wght@800&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;background:radial-gradient(ellipse at 50% 120%,#2a1a6b,transparent 60%),radial-gradient(ellipse at 85% 0%,#3a0f4d,transparent 55%),#07061a;color:#fff;font-family:Inter,sans-serif;position:relative;overflow:hidden}}
.t{{position:absolute;left:70px;top:90px;right:70px}}h1{{font-family:'Playfair Display',serif;font-size:96px;margin:0;line-height:1}}
.g{{background:linear-gradient(120deg,#ffc94d,#ff4fa3 50%,#8b5cff);-webkit-background-clip:text;color:transparent}}
p{{font-size:34px;color:#cfc9ff;margin:24px 0 0}}.b{{display:inline-block;margin-top:30px;padding:12px 26px;border-radius:99px;background:linear-gradient(120deg,#ffc94d,#ff4fa3);color:#14062b;font-weight:700;font-size:26px}}
.s{{position:absolute;bottom:0;left:0;width:100%}}.dot{{position:absolute;border-radius:50%}}</style></head><body>
<div class="t"><h1>NYE <span class="g">in Bali</span></h1><p>Beach clubs · Parties · Dinners · Fireworks<br>New Year's Eve {Y} in Bali</p><span class="b">Countdown to {NY} →</span></div>
{SKYLINE.replace('class="skyline"', 'class="s"')}
<script>for(let k=0;k<4;k++){{const cx=830+k*95,cy=90+(k%2)*110,c=['#ffc94d','#ff4fa3','#8b5cff','#41e3ff'][k];for(let i=0;i<48;i++){{const a=i/48*6.283,r=30+Math.random()*40,d=document.createElement('div');d.className='dot';d.style.cssText=`left:${{cx+Math.cos(a)*r}}px;top:${{cy+Math.sin(a)*r}}px;width:4px;height:4px;background:${{c}};box-shadow:0 0 8px ${{c}}`;document.body.appendChild(d)}}}}</script>
</body></html>"""


def build():
    if OUT.exists():
        og_keep = (OUT / "og.png").read_bytes() if (OUT / "og.png").exists() else None
        shutil.rmtree(OUT)
    else:
        og_keep = None
    OUT.mkdir()
    pages = {"/": page_home(), "/bali-fireworks-new-years-eve/": page_fireworks(),
             "/plan-your-night/": page_plan(), "/list-your-event/": page_list()}
    for c in CATEGORY_PAGES:
        pages[c["path"]] = page_category(c)
    for e in EVENTS:
        pages[f"/events/{e['slug']}/"] = page_event(e)
    for path, html in pages.items():
        f = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html)
    (OUT / "404.html").write_text(page_404())
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    shutil.copy(ROOT / "src" / "main.js", OUT / "main.js")
    (OUT / "favicon.svg").write_text(FAVICON)
    (OUT / "og.html").write_text(OG_HTML)
    if og_keep:
        (OUT / "og.png").write_bytes(og_keep)
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /og.html\n\nSitemap: {URL}/sitemap.xml\n")
    prio = lambda p: "1.0" if p == "/" else "0.6" if p.startswith("/events/") else "0.8"
    sm = "".join(
        f"<url><loc>{URL}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{prio(p)}</priority></url>\n"
        for p in pages
    )
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    build()

"""Rebrand the ported page: Viktor -> Starty wording, the Starty palette,
inline Starty marks in place of the Viktor logo images, section anchors for the
nav, and removal of the original header/footer (replaced by React components).

Runs after port.py (which invokes it). Pure stdlib except the optional PNG
recolour step, which needs Pillow (scripts/.venv)."""
import os, re, sys, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'public', 'assets')
CSS_DIR = os.path.join(ROOT, 'public', 'css')
BODY = os.path.join(ROOT, 'app', 'body.html')

# ---------------------------------------------------------------- palette
# Derived from the brand SVG: #0088FF blue, #0049A0 deep blue, #F0ABD5 pink, #FA8E59 orange.
COLOR_MAP = {
    # accent purple -> blue
    '6e47ff': '0088ff', '6748fd': '0088ff', '6c40ff': '0088ff', '6b40ff': '0088ff',
    '6441e8': '0079e6', '4e32b5': '0066c2', '3d278c': '0055a8', '2e1e6b': '003c7d',
    '8b6cff': '47a6ff', '8666ff': '47a6ff', '947fff': '47a6ff',
    '9e84ff': '7bbfff', '9fa2ff': '7bbfff',
    # lavender tints -> pink tints
    'bcaaff': 'f0abd5', 'bd96ff': 'f0abd5', 'aa99ff': 'f0abd5', 'e3acfd': 'f5bfe0',
    'd2c6ff': 'f5c6e3', 'f1edff': 'fdf0f7', 'f9f8ff': 'fdf7fb',
    # deep purple surfaces -> deep blue
    '150079': '0049a0', '150179': '0049a0', '1e0079': '0a4a9c', '20098a': '0b53ab',
    '2b129b': '0d5eb8', '3923b1': '1367c4', '4224bc': '1670cf', '5835de': '1f80e0',
    # peach -> orange
    'ffbb98': 'fa8e59', 'ffbd9e': 'fa9161', 'fdbca0': 'f99464', 'e8aa8a': 'e07f4d',
    'ffc9ad': 'fba77f', 'ffd1ba': 'fcb896', 'ffe0d0': 'fdd0b8', 'ffeadf': 'fde3d5', 'fff8f5': 'fff5ef',
}
HEX6 = re.compile(r'#([0-9a-fA-F]{6})(?![0-9a-fA-F])')
HEX8 = re.compile(r'#([0-9a-fA-F]{6})([0-9a-fA-F]{2})(?![0-9a-fA-F])')

import colorsys

def _shift(r, g, b):
    """Generic fallback for colours not in COLOR_MAP: purples -> blue (dark) or
    pink (light tints), matching the brand SVG. Returns None if not purple."""
    h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hue = h * 360
    if not (225 <= hue <= 292 and sat >= 0.15) or l < 0.16:   # leave near-black text alone
        return None
    if l > 0.72:
        nh = 328 / 360                      # pink tints (#F0ABD5 hue)
    else:
        nh = ((hue - 45) % 360) / 360       # blue
    nr, ng, nb = colorsys.hls_to_rgb(nh, l, sat)
    return int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255))

def _map_hex6(h):
    h = h.lower()
    if h in COLOR_MAP:
        return COLOR_MAP[h]
    rgb = _shift(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return '%02x%02x%02x' % rgb if rgb else h

def recolor(text):
    def sub8(m):
        return '#' + _map_hex6(m.group(1)) + m.group(2)
    def sub6(m):
        return '#' + _map_hex6(m.group(1))
    def sub_pct(m):                        # URL-encoded '#rrggbb' inside data: URIs
        return '%23' + _map_hex6(m.group(1))
    def sub_rgb(m):
        r, g, b = int(m.group(2)), int(m.group(3)), int(m.group(4))
        hx = '%02x%02x%02x' % (r, g, b)
        new = _map_hex6(hx)
        if new == hx:
            return m.group(0)
        nr, ng, nb = int(new[0:2], 16), int(new[2:4], 16), int(new[4:6], 16)
        return '%s(%d,%d,%d%s)' % (m.group(1), nr, ng, nb, m.group(5) or '')
    text = HEX8.sub(sub8, text)
    text = HEX6.sub(sub6, text)
    text = re.sub(r'%23([0-9a-fA-F]{6})(?![0-9a-fA-F])', sub_pct, text)
    text = re.sub(r'\b(rgba?)\((\d{1,3}),\s?(\d{1,3}),\s?(\d{1,3})(\s?,\s?[0-9.]+)?\)', sub_rgb, text)
    text = re.sub(r'#a9f(?![0-9a-fA-F])', '#f0abd5', text, flags=re.I)
    return text

def rebrand_words(text):
    text = text.replace('Viktor', 'Starty').replace('viktor', 'starty').replace('VIKTOR', 'STARTY')
    return text

def retagline(body):
    """Hero headline: 'Not a tool. / A hire.' -> Starty tagline."""
    return re.sub(r'Not a tool\.(<br[^>]*>)(<span[^>]*>)A hire\.</span>',
                  lambda m: 'Build. Work. Grow.' + m.group(1) + m.group(2) + 'Meet Starty.</span>', body, count=1)

def drop_brand_links(body):
    """Point every link that targeted viktor.com / app.viktor.com / the G2 listing at '#'."""
    return re.sub(r'href="https?://(?:[\w.-]*\.)?(?:viktor|starty)\.com[^"]*"|href="https?://www\.g2\.com/[^"]*"', 'href="#"', body)

# ---------------------------------------------------------------- copy
# Positioning from "Starty · Marketing & Brand Strategy · Q4 2026": Starty is the AI
# consumer app builder for creators, non-technical founders and product designers.
# Build (agents, models, templates, the builder) · Run (compute, data, security,
# auth, payments) · Grow (messaging, referrals, paid growth). Closing line:
# "Go outside. We will run the business. You go live your life."
# Pairs are applied verbatim to the rebranded body, in order.
COPY = [
    # hero
    ("Hire Starty and run your company like it's twice the size.", "Starty is the AI consumer app builder."),
    ("The AI employee that lives in Slack and Teams.", "Describe the app. Agents build it, run it and grow it. No code, no team."),
    ("Used by 50,000+ teams", "Used by 50,000+ builders"),
    # rotating band
    ("Starty is the AI employee that does the work you can't get to.", "Starty builds the consumer app you can't code yourself."),
    ("Starty is the AI employee that does the work you ", "Starty builds the consumer app you "),
    (">can't get to.<", ">can't code yourself.<"),
    (">can't justify hiring for.<", ">can't hire a team for.<"),
    (">shouldn't be doing yourself.<", ">keep putting off.<"),
    # workspace section
    ("workspace where people and agents do the work <span", "workspace where you and your agents run the app <span"),
    ("You set the direction, Starty does the legwork, across your tools, end to end. It proposes the next step and asks before anything it can't undo. You decide, it executes.",
     "You describe the app. Starty's agents build it, put it live and keep it running, with compute, data, sign-in and payments included. It proposes the next step and asks before anything it can't undo."),
    ("Probably our most intelligent team member. An AI employee connected to all our systems, right inside Slack.",
     "We shipped our first paid app in an afternoon. Starty built it, wired up payments and now runs it. We just watch the numbers in Slack."),
    (">Saved:<", ">Live in:<"),
    (">1-3 hours/week<", ">one afternoon<"),
    # features
    (">Employee, not software<", ">Build. Run. Grow.<"),
    ("What makes <span class=\"text-heading-gradient-dark\">Starty</span> a hire", "Everything your app needs, <span class=\"text-heading-gradient-dark\">in one place</span>"),
    ("Takes <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">ownership</span>",
     "Build <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">in minutes</span>"),
    ("Doesn't answer. Delivers. <br></span>Starty takes a task from research to shipped: decides, builds, updates your tools, hands back something you can use.",
     "Describe it. Ship it. <br></span>Agents, models and templates turn a prompt into a working consumer app, with a live link rather than a mockup."),
    ("Here's the weekly performance report you asked for.", "Your app is live. Here's the link and the first ten test users."),
    ("Works across <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">your company</span>",
     "Run <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">without ops</span>"),
    ("One employee. Every tool. <br></span>Starty works across Slack, Notion, HubSpot, Linear, Google Drive, and Stripe to finish work seamlessly.",
     "Compute, data, auth, payments. <br></span>Starty hosts the app, keeps the data safe, handles sign-in and takes payments through Stripe. Nothing for you to babysit."),
    ("Gets better <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">over time.</span>",
     "Grow <br aria-hidden=\"true\" class=\"hidden xl:block\"><span class=\"text-heading-gradient-dark\">on autopilot.</span>"),
    ("Learns your business. <br></span>Starty remembers your processes, decisions, and preferences, growing faster and more aligned over time.",
     "Messaging, referrals, paid growth. <br></span>Grow agents write the launch posts, run the referral loop and tune the paid spend, then report what moved and why."),
    ("Based on your past decisions, I've prepared 3 recommendations.", "Based on last week's installs, I've prepared 3 growth moves."),
    (">Q1 GTM strategy<", ">Referral loop<"),
    (">Hiring plan<", ">Launch campaign<"),
    (">Pricing update<", ">Pricing test<"),
    # compare
    ("<span class=\"block\">Starty delivers.</span>", "<span class=\"block\">Starty ships.</span>"),
    ("Other AI hands you a plan and waits. Starty does the thing and posts the result.",
     "Other AI hands you code and waits. Starty builds the app, puts it live and sends you the link."),
    (">Ad Spend Audit<", ">Building the app<"),
    (">Meeting Follow-ups<", ">Payments and sign-in<"),
    (">Workflow Automation<", ">Keeping it running<"),
    (">Building Tools<", ">Growing it<"),
    (">Tells you how to audit your ad spend.</p>", ">Writes a snippet. You wire up the rest.</p>"),
    (">Audits it.</span>Hands you the PDF.", ">Builds the whole app,</span>puts it live, sends you the link."),
    # how it works
    ("Plug-and-play. Live in <span class=\"text-integrations-hero-gradient\">two minutes.</span>",
     "From idea to live app in <span class=\"text-integrations-hero-gradient\">minutes.</span>"),
    (">Add to Slack or Teams<", ">Describe your app<"),
    ("Install Starty from the app directory. It shows up like any new teammate, ready to talk.",
     "Tell Starty what you want to build, in plain words. Start from a template or a blank prompt."),
    (">Connect your tools<", ">Watch it build<"),
    ("Link your CRM, Drive, calendar, and analytics. Each connection lets Starty act, not just read.",
     "Agents write the code, set up data, sign-in and payments, and put the app live on its own link."),
    (">Assign your first job<", ">Grow it<"),
    ("Give Starty a task that eats your week. It does it, then runs it on a schedule if you want.",
     "Starty runs the launch, referrals and paid growth, then reports what moved. You keep the users."),
    # security
    ("Starty asks before anything it cannot undo, and it pushes back when you are about to make a mistake. He proposes, you decide. Every sensitive action waits on your approval.",
     "Starty asks before anything it cannot undo, and pushes back when you are about to make a mistake. It proposes, you decide. Every sensitive action on your app waits for your approval."),
    ("Starty sees a channel's content only when it is invited.", "Agents get a hard spend ceiling and a human kill switch."),
    ("Per-person permissions and access controls.", "Your users' data stays in your app. Agents never see it."),
    # testimonials
    (">Trusted by 50,000+ teams<", ">Trusted by 50,000+ builders<"),
    ("The moment Starty becomes part of the team.", "The moment the app goes live."),
    ("Infrastructure for a $1M/yr agency built in 9 days", "A paid app live in 9 days"),
    ("“I discovered Starty 9 days ago, and I have already built the infrastructure for a $1,000,000 a year content agency with zero staff.”",
     "“I discovered Starty 9 days ago. I have already shipped a paid app, with sign-in and Stripe, and I have never written a line of code.”"),
    (">1 FTE/1 full time employee<", ">No dev team<"),
    ("“Literally a game-changer for me, like adding another employee (or two).”",
     "“Literally a game-changer. It is like having a dev team and a growth team without hiring either.”"),
    ("“Claude Tag writes better specs. Starty executes faster across tools. Starty actually goes and creates the tickets.”",
     "“Other tools give me code. Starty gives me a live app, and then it actually goes and gets users for it.”"),
    # closing CTA
    ("<span class=\"text-white\">One hire.</span> <span class=\"text-white\">The output of a team.</span>",
     "<span class=\"text-white\">Go outside.</span> <span class=\"text-white\">We will run the app.</span>"),
    ("Starty works nights, remembers every decision, and connects to 3,200 tools. Start free with $100 in credits, then $50 a month.",
     "Starty builds it, keeps it running and grows it while you live your life. Start free with $100 in credits, then $50 a month."),
]

META = {
    'title': 'Starty | The AI consumer app builder.',
    'description': 'Starty is the AI consumer app builder. Describe an app and agents build it, run it (compute, data, sign-in, payments) and grow it (messaging, referrals, paid growth). No code, no team. Start free.',
}

def recopy(body):
    missing = []
    for old, new in COPY:
        if old not in body:
            missing.append(old[:60]); continue
        body = body.replace(old, new)
    if missing:
        print('brand: %d copy strings not found:' % len(missing))
        for m in missing: print('   -', m)
    return body

# ---------------------------------------------------------------- Starty mark
def mark_svg(extra_attrs=''):
    """Inline SVG app icon: gradient tile with an S in the brand face."""
    return ('<svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Starty"%s>'
            '<defs><linearGradient id="startyGrad" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#0088FF"/><stop offset="0.55" stop-color="#0049A0"/><stop offset="1" stop-color="#FA8E59"/>'
            '</linearGradient></defs>'
            '<rect width="160" height="160" rx="40" fill="url(#startyGrad)"/>'
            '<text x="80" y="84" text-anchor="middle" dominant-baseline="central" fill="#fff" '
            'font-family="UlmGrotesk, Gellix, ui-sans-serif, system-ui, sans-serif" font-weight="700" font-size="104">S</text>'
            '</svg>') % (' ' + extra_attrs if extra_attrs else '')

def wordmark_span(color, size_px, extra_class=''):
    return ('<span class="%s" style="display:inline-block;font-family:UlmGrotesk,Gellix,ui-sans-serif,sans-serif;'
            'font-weight:700;font-size:%dpx;line-height:1;letter-spacing:-0.04em;color:%s">Starty</span>'
            % (extra_class, size_px, color))

def swap_brand_images(body):
    def attrs_of(tag):
        return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
    # app icon avatars
    def to_mark(m):
        a = attrs_of(m.group(0))
        keep = ' '.join('%s="%s"' % (k, a[k]) for k in ('class', 'width', 'height', 'style') if k in a)
        return mark_svg(keep)
    body = re.sub(r'<img[^>]*src="/assets/(?:type=Viktor\.png|typeViktor\.png|viktor-avatar-color\.svg)"[^>]*>', to_mark, body)
    # wordmarks
    def to_word(m):
        a = attrs_of(m.group(0))
        cls = a.get('class', '')
        cls = ' '.join(c for c in cls.split() if not c.startswith(('h-', 'w-')))
        white = 'pure-white' in a.get('src', '')
        size = 26 if white else 20
        return wordmark_span('#ffffff' if white else '#1a182b', size, cls)
    body = re.sub(r'<img[^>]*src="/assets/(?:viktor-logo-color\.svg|viktor-logo-pure-white\.svg|viktor-brand-light\.svg)"[^>]*>', to_word, body)
    return body

# ---------------------------------------------------------------- structure
def strip_chrome(body):
    body = re.sub(r'<header[^>]*data-site-header="true".*?</header>', '', body, count=1, flags=re.S)
    body = re.sub(r'<footer[^>]*data-site-footer="true".*?</footer>', '', body, count=1, flags=re.S)
    # mobile sticky signup banner (belongs to the original header/footer chrome)
    body = re.sub(r'<div class="fixed inset-x-0 bottom-3[^"]*">.*?</div></div></div>', '', body, count=1, flags=re.S)
    return body

ANCHORS = [  # (h2 text fragment, id)
    ('What makes', 'features'),
    ('A chatbot answers', 'compare'),
    ('Plug-and-play', 'how-it-works'),
    ('Autonomous, not unsupervised', 'security'),
    ('becomes part of the team', 'testimonials'),
]

def add_anchors(body):
    out = []; pos = 0
    for m in re.finditer(r'<section([^>]*)>', body):
        seg = body[m.end():m.end() + 20000]
        h2 = re.search(r'<h2[^>]*>(.*?)</h2>', seg, re.S)
        text = re.sub(r'<[^>]+>', '', h2.group(1)) if h2 else ''
        tag = m.group(0)
        if 'id="' not in m.group(1):
            for frag, sid in ANCHORS:
                if frag in text:
                    tag = '<section id="%s" style="scroll-margin-top:96px"%s>' % (sid, m.group(1))
                    break
        out.append(body[pos:m.start()]); out.append(tag); pos = m.end()
    out.append(body[pos:])
    return ''.join(out)

def _read_snippet(name):
    path = os.path.join(ROOT, 'scripts', name)
    if not os.path.exists(path):
        return None
    snippet = open(path, encoding='utf-8').read().strip()
    return re.sub(r'<!--.*?-->\s*', '', snippet, flags=re.S)

def _balanced_div_end(body, start):
    depth = 0
    for mm in re.finditer(r'<div\b|</div>', body[start:]):
        depth += 1 if mm.group(0).startswith('<div') else -1
        if depth == 0:
            return start + mm.end()
    return None

def insert_hero_tabs(body):
    """Build / Work / Grow segmented tabs at the top of the hero (scripts/hero-tabs.html)."""
    tabs = _read_snippet('hero-tabs.html')
    anchor = '<div class="flex w-full flex-col gap-10 lg:gap-14">'
    if not tabs or anchor not in body:
        return body
    return body.replace(anchor, anchor + tabs, 1)

def drop_hero_ctas(body):
    """Remove the hero's 'Get Started for Free' / 'Book a demo' button group (owner request)."""
    m = re.search(r'data-vk-label="Home Hero Vertical Get Started"', body)
    if not m:
        return body
    start = body.rfind('<div data-slot="button-group"', 0, m.start())
    end = _balanced_div_end(body, start)
    return body[:start] + body[end:] if start >= 0 and end else body

def drop_g2(body):
    """Remove every G2 rating badge (stars + '4.9 on G2') and the 'Users love … on G2'
    image in the testimonials header (owner request)."""
    while True:
        m = re.search(r'G2 rating: 4\.9 out of 5 stars</span></div>', body)
        if not m:
            break
        end = m.end(); depth = 0; start = None
        for mm in reversed(list(re.finditer(r'<div\b|</div>', body[:end]))):
            depth += 1 if mm.group(0) == '</div>' else -1
            if depth == 0:
                start = mm.start(); break
        if start is None:
            break
        body = body[:start] + body[end:]
    body = re.sub(r'<a [^>]*>\s*</a>', '', body)
    body = re.sub(r'<div class="\[&amp;_img\]:h-\[105px\][^"]*"><a title="Users love[^"]*".*?</a></div>', '', body, count=1, flags=re.S)
    return body

def replace_showcase(body):
    """Swap the Slack showcase inside the hero for the Starty app UI (scripts/hero-app.html)."""
    app = _read_snippet('hero-app.html')
    m = re.search(r'<div id="hero-app-showcase"[^>]*>', body)
    if not app or not m:
        return body
    end = _balanced_div_end(body, m.start())
    return body[:m.start()] + app + body[end:]

# ---------------------------------------------------------------- raster recolour
def recolor_pngs():
    try:
        from PIL import Image
    except ImportError:
        print('brand: Pillow not available, skipping PNG recolour (run with scripts/.venv/bin/python)')
        return
    lo, hi, shift = 160, 206, -32          # purple hue band (0-255 scale) -> rotate ~-45deg to blue
    n = 0
    for path in glob.glob(os.path.join(ASSETS, '*.png')):
        im = Image.open(path).convert('RGBA')
        r, g, b, a = im.split()
        hsv = Image.merge('RGB', (r, g, b)).convert('HSV')
        h, s, v = hsv.split()
        hp, sp = h.load(), s.load()
        w, ht = im.size
        for y in range(ht):
            for x in range(w):
                hv = hp[x, y]
                if lo <= hv <= hi and sp[x, y] > 20:
                    hp[x, y] = (hv + shift) % 256
        rgb = Image.merge('HSV', (h, s, v)).convert('RGB')
        rgb.putalpha(a)
        rgb.save(path)
        n += 1
    print('brand: recoloured %d PNGs' % n)

# ---------------------------------------------------------------- main
def main():
    body = open(BODY, encoding='utf-8').read()
    body = strip_chrome(body)
    body = swap_brand_images(body)
    body = add_anchors(body)
    body = replace_showcase(body)
    body = drop_hero_ctas(body)
    body = drop_g2(body)
    body = recolor(rebrand_words(body))
    body = drop_brand_links(body)
    body = retagline(body)
    body = recopy(body)
    open(BODY, 'w', encoding='utf-8').write(body)

    for f in glob.glob(os.path.join(CSS_DIR, '*.css')):
        s = open(f, encoding='utf-8').read()
        open(f, 'w', encoding='utf-8').write(recolor(s))
    for f in glob.glob(os.path.join(ASSETS, '*.svg')):
        s = open(f, encoding='utf-8').read()
        open(f, 'w', encoding='utf-8').write(recolor(s))

    meta_path = os.path.join(ROOT, 'app', 'meta.json')
    meta = json.load(open(meta_path))
    meta = {k: rebrand_words(v) for k, v in meta.items()}
    meta.update(META)
    json.dump(meta, open(meta_path, 'w'), indent=2)

    recolor_pngs()
    left = len(re.findall(r'viktor', body, re.I))
    print('brand: done | remaining "viktor" mentions in body:', left)

if __name__ == '__main__':
    main()

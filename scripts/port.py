"""Port the saved viktor.com page (../replica) into this Next.js app."""
import re, os, shutil, html, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(ROOT), 'replica')
HTML = os.path.join(SRC, 'Viktor _ Not a tool. A hire..html')
FILES = os.path.join(SRC, 'Viktor _ Not a tool. A hire._files')
PREFIX = './Viktor _ Not a tool. A hire._files/'

# 1. assets (everything except scripts / html)
for f in os.listdir(FILES):
    if f.endswith(('.js', '.html')) or f in ('js', '1496852565396661', '.DS_Store'):
        continue
    if f.endswith('.css'):
        css = open(os.path.join(FILES, f), encoding='utf-8').read()
        css = css.replace('../media/', '/fonts/media/')
        open(os.path.join(ROOT, 'public/css', f), 'w', encoding='utf-8').write(css)
    else:
        shutil.copy(os.path.join(FILES, f), os.path.join(ROOT, 'public/assets', f))

# 2. body html
s = open(HTML, encoding='utf-8').read()
body = s[s.index('<body'):]
body = body[body.index('>') + 1:]
body = body[:body.rindex('</body>')]
body = re.sub(r'<script\b[^>]*>.*?</script>', '', body, flags=re.S)
body = re.sub(r'<script\b[^>]*/>', '', body)
body = re.sub(r'<noscript>.*?</noscript>', '', body, flags=re.S)
body = re.sub(r'<iframe\b[^>]*>.*?</iframe>', '', body, flags=re.S)
body = re.sub(r'\s(srcset|sizes)="[^"]*"', '', body)
body = body.replace(PREFIX, '/assets/')
body = re.sub(r'/assets/companies/logos/', '/assets/', body)
# next/image proxied urls -> local asset by basename
def fix_next_image(m):
    url = html.unescape(m.group(1))
    q = re.search(r'url=([^&]*)', url)
    if q:
        from urllib.parse import unquote
        return 'src="/assets/' + os.path.basename(unquote(q.group(1))) + '"'
    return m.group(0)
body = re.sub(r'src="(/_next/image\?[^"]*)"', fix_next_image, body)
body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
open(os.path.join(ROOT, 'app/body.html'), 'w', encoding='utf-8').write(body.strip())

title = re.search(r'<title>([^<]*)</title>', s).group(1)
desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
open(os.path.join(ROOT, 'app/meta.json'), 'w').write(
    '{"title": %s, "description": %s}' % (repr(html.unescape(title)).replace("'", '"'), repr(html.unescape(desc)).replace("'", '"')))
print('body bytes', len(body), '| assets', len(os.listdir(os.path.join(ROOT, 'public/assets'))))
missing = [u for u in set(re.findall(r'/assets/([^"\')\s]+)', body)) if not os.path.exists(os.path.join(ROOT, 'public/assets', html.unescape(u)))]
print('missing assets:', missing)

# 3. Restore content the static snapshot did not contain -------------------
MD = os.path.join(ROOT, 'scripts', 'index.md')
body = open(os.path.join(ROOT, 'app/body.html'), encoding='utf-8').read()

def md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

if os.path.exists(MD):
    md = open(MD, encoding='utf-8').read()
    faq_md = md.split('## FAQ', 1)[1].split('\n---', 1)[0]
    faq_list = []                      # ordered (question, [paragraphs]); index.md is the source of truth
    for block in re.split(r'\n### ', '\n' + faq_md.strip()):
        block = block.strip()
        if not block or '\n' not in block:
            continue
        q, a = block.split('\n', 1)
        faq_list.append((html.unescape(q.strip()), [p.strip() for p in a.strip().split('\n\n') if p.strip()]))

    def set_trigger_text(item, q):
        """Replace the visible question inside the accordion trigger button."""
        def rep(mt):
            inner = re.sub(r'>([^<]{4,})<', lambda t: '>' + html.escape(q, quote=False) + '<', '>' + mt.group(2), count=1)[1:]
            return mt.group(1) + inner + mt.group(3)
        return re.sub(r'(data-slot="accordion-trigger"[^>]*>)(.*?)(</button>)', rep, item, count=1, flags=re.S)

    # The first (open) item keeps its snapshot markup: swap question + answer text in place
    if faq_list:
        om = re.search(r'<div[^>]*data-slot="accordion-item"[^>]*>(?:(?!data-slot="accordion-item").)*aria-expanded="true"(?:(?!data-slot="accordion-item").)*', body, re.S)
        if om:
            seg = set_trigger_text(om.group(0), faq_list[0][0])
            paras = iter(faq_list[0][1])
            seg = re.sub(r'(<p class="body-main text-secondary">)(.*?)(</p>)',
                         lambda mp: mp.group(1) + md_inline(next(paras, '')) + mp.group(3), seg, flags=re.S)
            body = body[:om.start()] + seg + body[om.end():]
    closed = {'i': 1}

    # FAQ answers for the closed accordion items
    def inject(m):
        item = m.group(0)
        if 'aria-expanded="true"' in item:
            return item
        trig = re.search(r'id="([^"]+)"', item)
        i = closed['i']; closed['i'] += 1
        if not trig or i >= len(faq_list):
            return item
        q, paras = faq_list[i]
        item = set_trigger_text(item, q)
        tid = trig.group(1); cid = tid[:-3] + 'H1_' if tid.endswith('H2_') else tid + '-content'
        item = item.replace('aria-expanded="false"', 'aria-expanded="false" aria-controls="%s"' % cid, 1)
        content = ('<div data-orientation="vertical" data-index="-1" data-closed="" hidden="" id="%s" aria-labelledby="%s" role="region" '
                   'style="--accordion-panel-height:auto;--accordion-panel-width:auto;animation-name:none" data-slot="accordion-content" '
                   'class="overflow-hidden text-sm [--tw-animation-duration:350ms] [--tw-duration:350ms] [--tw-ease:ease-in-out] data-open:animate-accordion-down data-closed:animate-accordion-up">'
                   '<div class="h-(--accordion-panel-height) pt-0 data-ending-style:h-0 data-starting-style:h-0 [&amp;_a]:underline [&amp;_a]:underline-offset-3 [&amp;_a]:hover:text-primitive-main-dark dark:hover:text-primitive-main-white [&amp;_p:not(:last-child)]:mb-4 px-6 pb-8">'
                   + ''.join('<p class="body-main text-secondary">%s</p>' % md_inline(p) for p in paras) + '</div></div>') % (cid, tid)
        return item.replace('</h3>', '</h3>' + content, 1)
    body, n = re.subn(r'<div[^>]*data-slot="accordion-item"[^>]*>(?:(?!data-slot="accordion-item").)*?</h3></div>', inject, body, flags=re.S)
    print('faq items processed', n, '| answers available', len(faq_list))

    # Comparison panels for the three tabs that were not rendered
    rows = re.findall(r'^\| (?!Task|-)([^|]+)\|([^|]+)\|([^|]+)\|', md, flags=re.M)
    panel = re.search(r'<div role="tabpanel" id="ad-spend-audit-comparison-panel".*?(?=<div role="tabpanel"|</section>)', body, re.S)
    if panel and len(rows) == 4:
        base = panel.group(0)
        # trim to the panel element itself by matching balanced divs
        depth = 0; end = None
        for mm in re.finditer(r'<div\b|</div>', base):
            depth += 1 if mm.group(0) == '<div' else -1
            if depth == 0:
                end = mm.end(); break
        base = base[:end]
        extra = ''
        for task, other, vik in rows[1:]:
            slug = re.sub(r'[^a-z0-9]+', '-', task.strip().lower()).strip('-')
            om = re.match(r'\s*\*\*(.+?)\*\*\s*—\s*(.*)', other.strip()); vm = re.match(r'\s*\*\*(.+?)\*\*\s*(.*)', vik.strip())
            p = base.replace('ad-spend-audit-comparison', slug + '-comparison')
            p = p.replace('<p class="', '<p data-cmp-tool class="', 1) if False else p
            p = re.sub(r'(<img alt="ChatGPT logo"[^>]*>)', '', p)
            p = re.sub(r'>ChatGPT</p>', '>%s</p>' % html.escape(om.group(1)), p, 1)
            p = re.sub(r'>Tells you how to audit your ad spend\.</p>', '>%s</p>' % md_inline(om.group(2)), p, 1)
            p = re.sub(r'>Audits it\.</span>Hands you the PDF\.', '>%s</span>%s' % (html.escape(vm.group(1)), md_inline(vm.group(2))), p, 1)
            p = p.replace('<div role="tabpanel"', '<div role="tabpanel" hidden=""', 1)
            extra += p
        body = body.replace(base, base + extra, 1)
        print('comparison panels added', len(rows) - 1)

open(os.path.join(ROOT, 'app/body.html'), 'w', encoding='utf-8').write(body)

# 4. Brand pass (Viktor -> Starty wording, palette, marks, nav/footer removal)
import subprocess
venv_py = os.path.join(ROOT, 'scripts', '.venv', 'bin', 'python')
subprocess.run([venv_py if os.path.exists(venv_py) else sys.executable, os.path.join(ROOT, 'scripts', 'brand.py')], check=True)

# Starty

Next.js (App Router) landing page for Starty, ported from the saved viktor.com page and rebranded.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## How it is built

- `scripts/port.py` reads the browser "Save as, complete" export in `../replica`, copies every image into `public/assets`, rewrites the three compiled Tailwind stylesheets into `public/css`, strips the original tracking and framework scripts, and writes the page markup to `app/body.html`. It restores content the static export did not contain (the 22 collapsed FAQ answers and the three unselected comparison tabs) from `scripts/index.md`, then runs `scripts/brand.py`.
- `scripts/brand.py` is the brand pass: swaps every "Viktor" for "Starty", remaps the purple/peach palette to the Starty palette (blue `#0088FF`, deep blue `#0049A0`, pink `#F0ABD5`, orange `#FA8E59`) across the CSS, inline styles and SVG assets, hue-shifts the purple in the PNG illustrations to blue (needs Pillow: `python3 -m venv scripts/.venv && scripts/.venv/bin/pip install pillow`), replaces the Viktor logo images with inline Starty marks, adds section anchors for the nav, points every former viktor.com / app.viktor.com / G2 link at `#`, and removes the original header and footer.
- `scripts/hero-tabs.html` (Build / Work / Grow segmented tabs, inserted at the top of the hero) and `scripts/hero-app.html` (the Starty app UI from the Figma "v2" frame, swapped in for the original Slack showcase) are spliced in by `brand.py`; icons live in `public/hero` (SVG exports from Figma, plus eight PNG crops of Figma's tile renders where the export returned a generic glyph); styles are the `.sh-*` rules in `public/brand.css`; tab behaviour and per-tab copy live in `app/interactive.tsx`.
- `components/SiteNav.tsx` is the ImagineArt landing-page kit navbar (`guidelines-for-landing-page`) adapted for Starty. `components/SiteFooter.tsx` is the kit's footer copied verbatim, with its assets under `public/media/footer`. Tailwind is installed only for that file: `app/tailwind.css` imports the theme and utilities layers without preflight and scans just the footer, so the ported page's compiled stylesheet is untouched.
- `components/StartyMark.tsx` holds the "S" app icon and the text wordmark. `public/brand.css` carries the few brand overrides.
- Kit adoption (`public/brand.css`, bottom block): body typography in Google Sans Flex with weights capped at 600 and the kit's text colours, headings kept in UlmGrotesk/Gellix, the 1240px container with 32px gutters (20px under 768px).
- `public/fonts` holds the site's web fonts (plus `google-sans-flex.woff2` from the kit) (Gellix, UlmGrotesk, Lato, Roboto Mono).
- `app/page.tsx` renders nav, `body.html`, and footer; `app/interactive.tsx` restores the client-side behaviour: FAQ accordion and "Show all", Slack/Teams toggle, comparison tabs and the rotating hero headline.

Re-run `python3 scripts/port.py` after changing anything in `../replica`, the colour map, or the wording rules.

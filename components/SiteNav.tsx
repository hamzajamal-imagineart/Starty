"use client";

/* Navbar from the ImagineArt landing-page kit (guidelines-for-landing-page),
   adapted for Starty: text wordmark instead of the ImagineArt SVG, Starty
   links, and the page's own typeface. Behaviour is unchanged: transparent at
   the top, compacts to a dark glass pill on scroll, hamburger below 1080px. */
import { useEffect, useState } from "react";
import { StartyWordmark } from "./StartyMark";

const FONT = "var(--font-sans), sans-serif";
const NAV_EASE = "cubic-bezier(0.22, 1, 0.36, 1)";
const NAV_DURATION = "480ms";

const HOME = "/";
const CTA_HREF = "https://app.starty.com/signup";

type NavLink = { label: string; href: string };

const NAV_LINKS: NavLink[] = [
  { label: "How It Works", href: "#how-it-works" },
  { label: "Features", href: "#features" },
  { label: "Compare", href: "#compare" },
  { label: "Security", href: "#security" },
  { label: "FAQ", href: "#faq" },
  { label: "Pricing", href: "#pricing" },
];

const isExternal = (href: string) => href.startsWith("http");

export function SiteNav({ variant = "onLight" }: { variant?: "onDark" | "onLight" } = {}) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 32);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const compact = scrolled;
  const darkTheme = compact || variant === "onDark";

  const themeVars = (
    darkTheme
      ? {
          "--nav-fg": "rgba(255,255,255,0.65)",
          "--nav-fg-hover": "#ffffff",
          "--nav-fg-ghost": "rgba(255,255,255,0.3)",
          "--nav-cta-bg": "#ffffff",
          "--nav-cta-fg": "#0A0A0B",
          "--nav-cta-glow": "rgba(255,255,255,0.08)",
          "--nav-burger": "rgba(255,255,255,0.9)",
          "--nav-logo": "#ffffff",
        }
      : {
          "--nav-fg": "rgba(11,11,12,0.6)",
          "--nav-fg-hover": "#0b0b0c",
          "--nav-fg-ghost": "rgba(11,11,12,0.28)",
          "--nav-cta-bg": "#0b0b0c",
          "--nav-cta-fg": "#ffffff",
          "--nav-cta-glow": "rgba(11,11,12,0.08)",
          "--nav-burger": "rgba(11,11,12,0.8)",
          "--nav-logo": "#1a182b",
        }
  ) as React.CSSProperties;

  return (
    <>
      <style>{`
        .nav-link { position: relative; display: inline-flex; flex-direction: column; height: 20px; overflow: hidden; cursor: pointer; text-decoration: none; }
        .nav-link-inner { display: flex; flex-direction: column; transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1); }
        .nav-link:hover .nav-link-inner { transform: translateY(-20px); }
        .nav-link-text { display: block; height: 20px; line-height: 20px; white-space: nowrap; font-family: ${FONT}; font-size: 15px; font-weight: 500; letter-spacing: 0.01em; color: var(--nav-fg); transition: color 0.3s; }
        .nav-link:hover .nav-link-text { color: var(--nav-fg-hover); }
        .nav-link-ghost { color: var(--nav-fg-ghost); }

        .nav-cta { font-family: ${FONT}; font-weight: 500; color: var(--nav-cta-fg); background: var(--nav-cta-bg); border: none; border-radius: 22px; cursor: pointer; letter-spacing: -0.01em; white-space: nowrap; transition: box-shadow 0.2s, transform 0.2s, background 0.3s, color 0.3s; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }
        .nav-cta:hover { box-shadow: 0 0 0 6px var(--nav-cta-glow); transform: scale(1.02); }

        .nav-logo { color: var(--nav-logo); transition: color 0.3s ease; display: flex; align-items: center; flex-shrink: 0; text-decoration: none; }

        .nav-desktop { display: flex; }
        .nav-burger { display: none; }
        @media (max-width: 1080px) {
          .nav-desktop { display: none !important; }
          .nav-burger { display: inline-flex !important; }
        }
        @keyframes navMenuIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
      `}</style>

      <nav
        style={{
          ...themeVars,
          position: "fixed",
          top: compact ? 16 : 12,
          left: 0,
          right: 0,
          marginInline: "auto",
          maxWidth: compact ? "min(1240px, calc(100vw - 32px))" : "100%",
          zIndex: 60,
          height: compact ? 72 : 64,
          paddingLeft: compact ? 28 : "max(32px, calc((100vw - 1240px) / 2 + 32px))",
          paddingRight: compact ? 16 : "max(32px, calc((100vw - 1240px) / 2 + 32px))",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 16,
          background: compact ? "rgba(10,10,11,0.42)" : "transparent",
          backdropFilter: compact ? "blur(32px) saturate(180%)" : "blur(20px)",
          WebkitBackdropFilter: compact ? "blur(32px) saturate(180%)" : "blur(20px)",
          borderRadius: compact ? 999 : 0,
          boxShadow: scrolled
            ? "0 20px 48px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 1px rgba(255,255,255,0.1)"
            : "none",
          boxSizing: "border-box",
          transition: [
            `top ${NAV_DURATION} ${NAV_EASE}`,
            `max-width ${NAV_DURATION} ${NAV_EASE}`,
            `padding ${NAV_DURATION} ${NAV_EASE}`,
            `height ${NAV_DURATION} ${NAV_EASE}`,
            `border-radius ${NAV_DURATION} ${NAV_EASE}`,
            `background 320ms ease`,
            `box-shadow ${NAV_DURATION} ease`,
          ].join(", "),
        }}
      >
        <a href={HOME} className="nav-logo" aria-label="Starty home">
          <StartyWordmark size={26} />
        </a>

        <div className="nav-desktop" style={{ alignItems: "center", gap: "clamp(14px, 1.4vw, 22px)" }}>
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="nav-link"
              {...(isExternal(link.href) ? { target: "_blank", rel: "noopener noreferrer" } : {})}
            >
              <span className="nav-link-inner">
                <span className="nav-link-text">{link.label}</span>
                <span className="nav-link-text nav-link-ghost">{link.label}</span>
              </span>
            </a>
          ))}
        </div>

        <div className="nav-desktop" style={{ alignItems: "center", gap: 10, flexShrink: 0 }}>
          <a href={CTA_HREF} className="nav-cta" style={{ height: 40, padding: "8px 16px", fontSize: 16 }}>
            Get Started
          </a>
        </div>

        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="nav-burger"
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            border: "none",
            background: "transparent",
            color: "var(--nav-burger)",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
          aria-label="Open menu"
        >
          <span style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            <span style={{ display: "block", width: 18, height: 1.5, borderRadius: 2, background: "currentColor", transition: "transform 250ms ease", transform: menuOpen ? "translateY(3.25px) rotate(45deg)" : "none" }} />
            <span style={{ display: "block", width: 18, height: 1.5, borderRadius: 2, background: "currentColor", transition: "transform 250ms ease", transform: menuOpen ? "translateY(-3.25px) rotate(-45deg)" : "none" }} />
          </span>
        </button>
      </nav>

      {menuOpen && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 101,
            background: "#fff",
            display: "flex",
            flexDirection: "column",
            animation: "navMenuIn 0.22s cubic-bezier(0.4,0,0.2,1) forwards",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "18px 24px", flexShrink: 0 }}>
            <a href={HOME} onClick={() => setMenuOpen(false)} style={{ display: "inline-flex", alignItems: "center", color: "#1a182b", textDecoration: "none" }} aria-label="Starty home">
              <StartyWordmark size={26} />
            </a>
            <button
              onClick={() => setMenuOpen(false)}
              style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 4, border: "none", background: "transparent", color: "rgba(11,11,12,0.6)", cursor: "pointer" }}
              aria-label="Close menu"
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M3 3l12 12M15 3L3 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>

          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", paddingBottom: 40 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={() => setMenuOpen(false)}
                  {...(isExternal(link.href) ? { target: "_blank", rel: "noopener noreferrer" } : {})}
                  style={{
                    display: "block",
                    textAlign: "center",
                    padding: "10px 32px",
                    borderRadius: 10,
                    fontFamily: FONT,
                    fontSize: 22,
                    fontWeight: 400,
                    letterSpacing: "-0.2px",
                    color: "rgba(11,11,12,0.7)",
                    textDecoration: "none",
                  }}
                >
                  {link.label}
                </a>
              ))}
            </div>

            <div style={{ width: "calc(100% - 48px)", height: 1, background: "rgba(11,11,12,0.08)", margin: "16px 0" }} />

            <a
              href={CTA_HREF}
              onClick={() => setMenuOpen(false)}
              style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", height: 46, padding: "0 26px", borderRadius: 22, fontFamily: FONT, fontSize: 15, fontWeight: 600, color: "#fff", background: "#171717", textDecoration: "none" }}
            >
              Get Started
            </a>
          </div>
        </div>
      )}
    </>
  );
}

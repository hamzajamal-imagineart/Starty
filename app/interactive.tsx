"use client";
import { useEffect } from "react";

/**
 * Restores the interactive behaviour of the original page on top of the
 * static markup rendered by page.tsx (accordion, tabs, dropdown menus,
 * the rotating hero headline and the FAQ "show all" toggle).
 */
export default function Interactive() {
  useEffect(() => {
    const cleanups: Array<() => void> = [];
    const on = <K extends keyof HTMLElementEventMap>(
      el: Element | Window,
      ev: K,
      fn: (e: HTMLElementEventMap[K]) => void,
    ) => {
      el.addEventListener(ev, fn as EventListener);
      cleanups.push(() => el.removeEventListener(ev, fn as EventListener));
    };

    /* ---------------- FAQ accordion ---------------- */
    const setOpen = (item: Element, open: boolean) => {
      const parts = [item, item.querySelector("h3"), item.querySelector("[data-slot=accordion-trigger]"), item.querySelector("[data-slot=accordion-content]")];
      for (const p of parts) {
        if (!p) continue;
        p.toggleAttribute("data-open", open);
        p.toggleAttribute("data-closed", !open);
      }
      item.querySelector("[data-slot=accordion-trigger]")?.setAttribute("aria-expanded", String(open));
      const content = item.querySelector<HTMLElement>("[data-slot=accordion-content]");
      if (content) {
        content.style.animationName = "none";
        content.hidden = !open;
      }
    };
    document.querySelectorAll("[data-slot=accordion-trigger]").forEach((btn) => {
      on(btn, "click", () => {
        const item = btn.closest("[data-slot=accordion-item]");
        if (!item) return;
        const willOpen = btn.getAttribute("aria-expanded") !== "true";
        item.parentElement?.closest("[data-slot=accordion]")?.querySelectorAll("[data-slot=accordion-item]").forEach((i) => i !== item && setOpen(i, false));
        setOpen(item, willOpen);
      });
    });

    /* ---------------- FAQ "Show all" ---------------- */
    const showAll = Array.from(document.querySelectorAll("button")).find((b) => /Show All \d+ Questions/.test(b.textContent ?? ""));
    if (showAll) {
      const label = showAll.textContent ?? "";
      const grid = showAll.closest("section")?.querySelector<HTMLElement>(".grid-rows-\\[0fr\\]");
      const wrappers = grid ? Array.from(grid.querySelectorAll<HTMLElement>(":scope > div > div")) : [];
      on(showAll, "click", () => {
        const expand = showAll.getAttribute("aria-expanded") !== "true";
        showAll.setAttribute("aria-expanded", String(expand));
        showAll.textContent = expand ? "Show Less" : label;
        grid?.classList.toggle("grid-rows-[0fr]", !expand);
        grid?.classList.toggle("grid-rows-[1fr]", expand);
        wrappers.forEach((w, i) => {
          w.style.transitionDelay = expand ? `${i * 40}ms` : "0ms";
          w.classList.toggle("opacity-0", !expand);
          w.classList.toggle("blur-md", !expand);
          w.classList.toggle("-translate-y-2", !expand);
          w.classList.toggle("opacity-100", expand);
          w.classList.toggle("blur-0", expand);
          w.classList.toggle("translate-y-0", expand);
        });
      });
    }

    /* ---------------- Tabs ---------------- */
    const SELECTED = ["text-contrast", "bg-primitive-main-dark", "md:bg-none"];
    const UNSELECTED = ["bg-secondary", "text-primary"];
    document.querySelectorAll<HTMLElement>("[role=tablist]").forEach((list) => {
      const tabs = Array.from(list.querySelectorAll<HTMLElement>("[role=tab]"));
      const indicator = list.querySelector<HTMLElement>(":scope > span[aria-hidden]");
      const isPlatform = list.getAttribute("aria-label") === "Switch app preview";
      const moveIndicator = (tab: HTMLElement) => {
        if (!indicator || isPlatform) return;
        indicator.style.width = `${tab.offsetWidth}px`;
        indicator.style.height = `${tab.offsetHeight}px`;
        indicator.style.transform = `translate(${tab.offsetLeft}px, ${tab.offsetTop}px)`;
      };
      tabs.forEach((tab, idx) => {
        on(tab, "click", () => {
          tabs.forEach((t) => {
            const sel = t === tab;
            t.setAttribute("aria-selected", String(sel));
            if (t.hasAttribute("tabindex")) t.tabIndex = sel ? 0 : -1;
            if (isPlatform) {
              t.classList.toggle("text-secondary", !sel);
              t.classList.toggle("text-primary", sel);
            } else if (indicator) {
              SELECTED.forEach((c) => t.classList.toggle(c, sel));
              UNSELECTED.forEach((c) => t.classList.toggle(c, !sel));
            }
            const panel = t.getAttribute("aria-controls") && document.getElementById(t.getAttribute("aria-controls")!);
            if (panel && panel.getAttribute("role") === "tabpanel") panel.hidden = !sel;
          });
          if (isPlatform) list.style.setProperty("--platform-toggle-index", String(idx));
          moveIndicator(tab);
        });
      });
      const current = tabs.find((t) => t.getAttribute("aria-selected") === "true");
      if (current) {
        moveIndicator(current);
        on(window, "resize", () => moveIndicator(tabs.find((t) => t.getAttribute("aria-selected") === "true") ?? current));
      }
    });

    /* ---------------- Rotating hero headline ---------------- */
    const rotWrap = Array.from(document.querySelectorAll<HTMLElement>("span[aria-hidden]")).find((s) =>
      s.children.length > 1 && Array.from(s.children).every((c) => /translate3d/.test((c as HTMLElement).style.transform)),
    );
    if (rotWrap) {
      const lines = Array.from(rotWrap.children) as HTMLElement[];
      let i = lines.findIndex((l) => l.style.opacity === "1");
      if (i < 0) i = 0;
      const show = (el: HTMLElement, state: "in" | "out" | "wait") => {
        el.style.transition = "transform 0.6s cubic-bezier(0.77, 0, 0.175, 1), opacity 0.3s linear, filter 108ms cubic-bezier(0.2, 0.85, 0.25, 1)";
        el.style.transform = state === "in" ? "translate3d(0px, 0%, 0px)" : state === "out" ? "translate3d(0px, -100%, 0px)" : "translate3d(0px, 100%, 0px)";
        el.style.opacity = state === "in" ? "1" : "0";
      };
      const id = window.setInterval(() => {
        const prev = lines[i];
        i = (i + 1) % lines.length;
        show(prev, "out");
        show(lines[i], "wait");
        requestAnimationFrame(() => requestAnimationFrame(() => show(lines[i], "in")));
        window.setTimeout(() => show(prev, "wait"), 650);
      }, 3200);
      cleanups.push(() => window.clearInterval(id));
    }

    /* ---------------- Header dropdown menus ---------------- */
    document.querySelectorAll<HTMLElement>("header button[aria-haspopup=menu]").forEach((btn) => {
      const wrap = btn.parentElement;
      const menu = wrap?.querySelector<HTMLElement>("[role=menu]");
      const holder = menu?.parentElement;
      if (!wrap || !menu || !holder) return;
      let timer = 0;
      const toggle = (open: boolean) => {
        btn.setAttribute("aria-expanded", String(open));
        holder.classList.toggle("pointer-events-none", !open);
        holder.classList.toggle("pointer-events-auto", open);
        menu.toggleAttribute("inert", !open);
        menu.setAttribute("aria-hidden", String(!open));
        menu.style.transform = open ? "scale(1)" : "scale(0.9)";
        menu.style.opacity = open ? "1" : "0";
      };
      on(wrap, "mouseenter", () => { window.clearTimeout(timer); toggle(true); });
      on(wrap, "mouseleave", () => { timer = window.setTimeout(() => toggle(false), 120); });
      on(btn, "click", () => toggle(btn.getAttribute("aria-expanded") !== "true"));
      on(wrap, "focusout", (e) => { if (!wrap.contains((e as FocusEvent).relatedTarget as Node)) toggle(false); });
    });

    /* ---------------- Smooth in-page anchors ---------------- */
    document.querySelectorAll<HTMLAnchorElement>('a[href^="https://viktor.com/#"], a[href^="#"]').forEach((a) => {
      const hash = a.getAttribute("href")!.split("#")[1];
      if (!hash) return;
      a.setAttribute("href", `#${hash}`);
    });

    return () => cleanups.forEach((fn) => fn());
  }, []);
  return null;
}

import type { CSSProperties } from "react";

const BRAND_FONT = "UlmGrotesk, Gellix, ui-sans-serif, system-ui, sans-serif";

/** App-icon style mark: gradient tile with an "S" in the brand face. */
export function StartyMark({ size = 28, style, className }: { size?: number; style?: CSSProperties; className?: string }) {
  return (
    <svg viewBox="0 0 160 160" width={size} height={size} role="img" aria-label="Starty" className={className} style={style}>
      <defs>
        <linearGradient id="startyGradMark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#0088FF" />
          <stop offset="0.55" stopColor="#0049A0" />
          <stop offset="1" stopColor="#FA8E59" />
        </linearGradient>
      </defs>
      <rect width="160" height="160" rx="40" fill="url(#startyGradMark)" />
      <text x="80" y="84" textAnchor="middle" dominantBaseline="central" fill="#fff" fontFamily={BRAND_FONT} fontWeight={700} fontSize={104}>
        S
      </text>
    </svg>
  );
}

/** Text wordmark in the brand face. Colour is inherited unless given. */
export function StartyWordmark({ size = 24, color, style }: { size?: number; color?: string; style?: CSSProperties }) {
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: BRAND_FONT,
        fontWeight: 700,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: "-0.04em",
        color: color ?? "inherit",
        ...style,
      }}
    >
      Starty
    </span>
  );
}

// Generate Tailwind utilities for the kit footer and scope every selector to
// #kit-footer so nothing leaks into the ported page (whose own compiled
// Tailwind uses the same class names). Output: public/css/footer.css
import { execSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import postcss from "postcss";

const input = `
@import "tailwindcss/theme.css" source(none);
@import "tailwindcss/utilities.css" source(none);
@source "../components/SiteFooter.tsx";
`;
mkdirSync(".tmp", { recursive: true });
writeFileSync(".tmp/footer.in.css", input.replace('"../components', '"../components'));
execSync("npx @tailwindcss/cli -i .tmp/footer.in.css -o .tmp/footer.out.css", { stdio: "inherit" });

const root = postcss.parse(readFileSync(".tmp/footer.out.css", "utf8"));
const SCOPE = "#kit-footer";
root.walkRules((rule) => {
  if (rule.parent?.type === "atrule" && /keyframes|property/.test(rule.parent.name)) return;
  rule.selectors = rule.selectors.map((s) => {
    const t = s.trim();
    if (t === ":root" || t === ":host" || t === ":root, :host") return `${SCOPE}`;
    if (t.startsWith("*") || t.startsWith("::")) return `${SCOPE} ${t}`;
    return `${SCOPE} ${t}`;
  });
});
// flatten @layer blocks so the rules are unlayered (they carry an ID selector anyway)
root.walkAtRules("layer", (at) => { if (at.nodes) at.replaceWith(at.nodes); else at.remove(); });
writeFileSync("public/css/footer.css", root.toString());
console.log("footer.css written:", root.toString().length, "bytes");

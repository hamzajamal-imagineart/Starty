import fs from "node:fs";
import path from "node:path";
import Interactive from "./interactive";
import { SiteNav } from "@/components/SiteNav";
import { SiteFooter } from "@/components/SiteFooter";

export default function Home() {
  const body = fs.readFileSync(path.join(process.cwd(), "app", "body.html"), "utf-8");
  return (
    <>
      <SiteNav variant="onLight" />
      <div style={{ display: "contents" }} suppressHydrationWarning dangerouslySetInnerHTML={{ __html: body }} />
      <div id="kit-footer" style={{ display: "contents" }}>
        <SiteFooter />
      </div>
      <Interactive />
    </>
  );
}

import type { Metadata } from "next";
import meta from "./meta.json";

export const metadata: Metadata = {
  title: meta.title,
  description: meta.description,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-US" dir="ltr" className="font-sans antialiased" data-page-layout="site">
      <head>
        <link rel="stylesheet" href="/css/3873u70m3r4xi.css" />
        <link rel="stylesheet" href="/css/1pg1yw1zv3i8s.css" />
        <link rel="stylesheet" href="/css/0nbutxshy069f.css" />
        <link rel="stylesheet" href="/css/footer.css" />
        <link rel="stylesheet" href="/brand.css" />
      </head>
      <body data-testid="root-body">{children}</body>
    </html>
  );
}

// Asset URL helper for static-export deploys mounted under a basePath.
// Next.js prefixes basePath onto URLs it generates, but not onto hand-written
// /public asset strings. Route every such path through withBasePath().

export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Prefix a root-relative /public asset path with the mount basePath. */
export const withBasePath = (p: string): string =>
  p.startsWith("/") ? `${BASE_PATH}${p}` : p;

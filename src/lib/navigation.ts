/**
 * Navigation principale : source unique pour le Header et le Footer.
 * Ordre et libellés issus de l'architecture de l'information (design, planche 0).
 */
export interface NavLink {
  href: string;
  label: string;
}

export const NAV_LINKS: NavLink[] = [
  { href: "/sorties", label: "Sorties" },
  { href: "/groupes", label: "Groupes" },
  { href: "/qui-je-suis", label: "Qui je suis" },
  { href: "/carnet", label: "Carnet" },
];

export const CONTACT_LINK: NavLink = { href: "/contact", label: "Me contacter" };

/**
 * Un lien est actif sur sa propre page et sur toutes ses sous-pages :
 * « Carnet » reste actif sur /carnet/un-article.
 */
export function isActive(pathname: string, href: string): boolean {
  // Astro peut fournir l'URL avec ou sans « / » final selon la config.
  const path = pathname.length > 1 ? pathname.replace(/\/$/, "") : pathname;

  if (href === "/") return path === "/";
  return path === href || path.startsWith(`${href}/`);
}

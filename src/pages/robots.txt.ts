import type { APIRoute } from "astro";

/**
 * robots.txt généré au build à partir de `site` (astro.config.mjs),
 * pour n'avoir qu'une seule source de vérité sur le domaine.
 *
 * On autorise tout : robots.txt gère l'exploration, pas l'indexation.
 * Bloquer une URL empêcherait Google de voir ses redirections ou un
 * éventuel `noindex`. Pour exclure une page de l'index, utiliser `noindex`.
 */
const getRobotsTxt = (sitemapURL: URL) => `User-agent: *
Allow: /

Sitemap: ${sitemapURL.href}
`;

export const GET: APIRoute = ({ site }) => {
  // `site` vaut undefined si la propriété est absente de la config :
  // on échoue au build plutôt que de publier une ligne Sitemap invalide.
  if (!site) {
    throw new Error("robots.txt : définir `site` dans astro.config.mjs.");
  }

  const sitemapURL = new URL("sitemap-index.xml", site);

  return new Response(getRobotsTxt(sitemapURL), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};

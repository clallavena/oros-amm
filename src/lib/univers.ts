/**
 * Les univers de sortie : source unique de vérité.
 * Réutilisé par BaseLayout (thème) et, au lot 3, par le schéma
 * de la collection `sorties` : z.enum(UNIVERS).
 */
export const UNIVERS = ["forest", "snow", "sunset"] as const;

export type Univers = (typeof UNIVERS)[number];

/**
 * Couleur de la barre du navigateur mobile pour chaque univers.
 * Valeurs = la couleur `primary` de l'univers (voir global.css).
 */
export const THEME_COLOR: Record<Univers, string> = {
  forest: "#295943",
  snow: "#23517a",
  sunset: "#753061",
};

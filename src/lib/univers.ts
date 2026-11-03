/**
 * Deux notions distinctes, à ne pas confondre :
 *
 * - le THÈME : l'ambiance visuelle (couleurs). Il s'applique à n'importe
 *   quelle page via <BaseLayout theme="…">.
 * - l'UNIVERS : une catégorie de sorties, qui apparaît dans les URL
 *   (/sorties/randonnee/…). Chaque univers a UN thème.
 *
 * « forest » est à la fois le thème de la marque (accueil, groupes…)
 * et celui de l'univers Randonnée : c'est pour ça qu'on ne fusionne pas
 * les deux notions.
 */

/* ---------- Thèmes ---------- */

export const THEMES = ["forest", "snow", "sunset"] as const;

export type Theme = (typeof THEMES)[number];

/**
 * Couleur de la barre du navigateur mobile pour chaque thème.
 * Valeurs = la couleur `primary` du thème (voir global.css).
 */
export const THEME_COLOR: Record<Theme, string> = {
  forest: "#295943",
  snow: "#23517a",
  sunset: "#753061",
};

/* ---------- Univers ---------- */

/** Utilisé tel quel dans les URL : ne pas mettre d'accents ni d'espaces. */
export const UNIVERS = ["randonnee", "hiver", "itinerance"] as const;

export type Univers = (typeof UNIVERS)[number];

export interface UniversInfo {
  label: string;
  theme: Theme;
  /** Phrase d'accroche (textes du design, planche « Hub Sorties »). */
  accroche: string;
}

/*
 * Record<Univers, …> : TypeScript refuse de compiler si un univers
 * de la liste n'a pas son entrée ici (même idée qu'un switch exhaustif).
 */
export const UNIVERS_INFO: Record<Univers, UniversInfo> = {
  randonnee: {
    label: "Randonnée & découverte",
    theme: "forest",
    accroche:
      "Marcher pour comprendre : faune, flore, paysages et vie du milieu montagnard.",
  },
  hiver: {
    label: "Hiver & raquettes",
    theme: "snow",
    accroche:
      "Forêts enneigées, traces d'animaux et silence feutré, sans technique de ski. En binôme avec un accompagnateur diplômé.",
  },
  itinerance: {
    label: "Itinérance & refuges",
    theme: "sunset",
    accroche:
      "Plusieurs jours de marche, de refuge en refuge, et le lever du jour là-haut.",
  },
};

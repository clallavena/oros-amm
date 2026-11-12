/**
 * Thématiques de découverte : le fil conducteur d'une sortie
 *
 * À ne pas confondre avec les THÈMES de lib/univers.ts, qui sont des
 * ambiances visuelles (forest, snow, sunset). D'où le nom « thématique ».
 *
 * Une thématique n'appartient à aucun univers : « Faune » peut être le fil
 * d'une randonnée d'été comme d'une sortie raquettes (traces dans la neige).
 */

/** Utilisé dans le frontmatter et dans l'URL (?thematique=faune) : pas d'accents. */
export const THEMATIQUES = ["faune", "flore", "milieu", "vie-en-montagne"] as const;

export type Thematique = (typeof THEMATIQUES)[number];

export interface ThematiqueInfo {
  label: string;
  /** Une phrase, affichée sur la carte de la thématique. */
  description: string;
  /** Pictogramme : attribut `d` d'un <path> SVG 24×24 en trait (design). */
  icone: string;
}

export const THEMATIQUE_INFO: Record<Thematique, ThematiqueInfo> = {
  faune: {
    label: "Faune",
    description:
      "Traces, indices de présence, observation à distance : apprendre à voir sans déranger.",
    // empreinte
    icone:
      "M12 11c2.2 0 4 2 4 4.5S14.2 20 12 20s-4-2-4-4.5S9.8 11 12 11zM6 7.2a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6zM10 3.7a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6zM14 3.7a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6zM18 7.2a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6z",
  },
  flore: {
    label: "Flore",
    description:
      "Fleurs d'altitude, arbres, plantes et leurs usages : reconnaître ce qui pousse sous nos pas.",
    // feuille d'érable (grille 24 × 24, en trait comme les autres pictos)
    icone:
      "M12 2l1.5 3 2-.5-.5 4.5 2.5-2 .5 1.5 3-.5-1 3 1.5 1-4.5 3.5.5 1.5-4.7-.7H11.2l-4.7.7.5-1.5L2.5 12 4 11l-1-3 3 .5.5-1.5 2.5 2-.5-4.5 2 .5zM12 22V8",
  },
  milieu: {
    label: "Milieu montagnard",
    description:
      "Lire un paysage, comprendre la roche, l'eau, les étages de végétation et la météo.",
    // relief
    icone: "M2 20 9 7l4 7 2-3 7 9zM7.5 10l1.5 1.5L10.5 10",
  },
  "vie-en-montagne": {
    label: "Vie en montagne",
    description:
      "Alpages, pastoralisme, chalets d'estive : comment les hommes vivent la montagne.",
    // chalet
    icone: "M3 20h18M5 20v-8l7-5 7 5v8M10 20v-5h4v5",
  },
};

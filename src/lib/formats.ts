/**
 * Valeurs et libellés des sorties. Fichier « pur » (aucun import Astro) :
 * il peut être importé aussi bien par content.config.ts que par les pages.
 */

/* ---------- Formats ---------- */

export const FORMATS = ["demi-journee", "journee", "itinerance", "sur-mesure"] as const;

export type Format = (typeof FORMATS)[number];

export const FORMAT_LABEL: Record<Format, string> = {
  "demi-journee": "Demi-journée",
  journee: "Journée",
  itinerance: "Itinérance",
  "sur-mesure": "Sur mesure",
};

/* ---------- Niveaux ---------- */

export const NIVEAUX = ["facile", "modere", "soutenu", "adapte"] as const;

export type Niveau = (typeof NIVEAUX)[number];

export const NIVEAU_LABEL: Record<Niveau, string> = {
  facile: "Facile",
  modere: "Modéré",
  soutenu: "Soutenu",
  adapte: "Adapté à votre niveau",
};

/* ---------- Comparatif des formats (hub /sorties) ---------- */

export interface FormatInfo {
  /** Ordre de grandeur, pas une promesse : chaque fiche donne sa vraie durée. */
  duree: string;
  effort: Niveau;
  idealPour: string;
  /**
   * Libellé imposé pour la ligne « Univers ». Sinon, la ligne est calculée
   * à partir des sorties publiées (voir resumer() dans sorties.ts).
   */
  universFixe?: string;
}

// TODO : confirmer les durées de la demi-journée et de la journée.
export const FORMAT_INFO: Record<Format, FormatInfo> = {
  "demi-journee": {
    duree: "≈ 3 h de marche",
    effort: "facile",
    idealPour: "Familles, première fois",
  },
  journee: {
    duree: "≈ 5 à 6 h de marche",
    effort: "modere",
    idealPour: "Marcheurs réguliers",
  },
  itinerance: {
    duree: "2 à 5 jours",
    effort: "soutenu",
    idealPour: "Randonneurs entraînés",
  },
  "sur-mesure": {
    duree: "Selon vos envies",
    effort: "adapte",
    idealPour: "Solo, amis, famille",
    universFixe: "Tous",
  },
};

/* ---------- Mise en forme ---------- */

const euros = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

const nombres = new Intl.NumberFormat("fr-FR");

/** 35 → « 35 € » (espace insécable incluse, comme l'exige la typographie française). */
export const formatPrix = (montant: number): string => euros.format(montant);

/** 2100 → « 2 100 » */
export const formatNombre = (n: number): string => nombres.format(n);

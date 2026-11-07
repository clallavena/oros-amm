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

/*
 * Dates des départs. timeZone fixé : le site est généré au build, et la
 * machine qui build (ton PC, un serveur d'intégration…) n'est pas forcément
 * à l'heure de Paris. Sans ça, une date pourrait s'afficher la veille.
 */
const jourCourt = new Intl.DateTimeFormat("fr-FR", {
  weekday: "short",
  day: "numeric",
  month: "long",
  timeZone: "Europe/Paris",
});

const memeJour = (a: Date, b: Date): boolean =>
  jourCourt.format(a) === jourCourt.format(b);

/** « sam. 14 juin » ou « sam. 14 juin → dim. 15 juin » */
export function formatPeriode(debut: Date, fin?: Date): string {
  if (fin === undefined || memeJour(debut, fin)) return jourCourt.format(debut);
  return `${jourCourt.format(debut)} → ${jourCourt.format(fin)}`;
}

/** 0 → « Complet », 1 → « 1 place », 5 → « 5 places » */
export function formatPlaces(places: number): string {
  if (places === 0) return "Complet";
  return `${places} place${places > 1 ? "s" : ""}`;
}

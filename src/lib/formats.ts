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

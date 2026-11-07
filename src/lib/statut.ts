/**
 * Statut d'accompagnateur en montagne stagiaire : source unique.
/* ---------- Titre affiché ---------- */

/** Titre réglementaire, en minuscules : à utiliser en milieu de phrase. */
export const TITRE = "accompagnateur en montagne stagiaire";

/** Même titre avec une majuscule : début de phrase, titres de page, sous-titres. */
export const TITRE_MAJ = TITRE.charAt(0).toUpperCase() + TITRE.slice(1);

/* ---------- Modalités d'encadrement ---------- */

/** Ce que mon statut me permet aujourd'hui pour un type de sortie. */
export const MODALITES = ["autonomie", "binome", "apres-diplome"] as const;

export type Modalite = (typeof MODALITES)[number];

/*
 * Le libellé porte le sens : le tableau doit se comprendre sans la couleur
 * ni l'icône (WCAG 1.4.1).
 */
export const MODALITE_LIBELLE: Record<Modalite, string> = {
  autonomie: "Oui, en autonomie",
  binome: "En binôme avec un diplômé, à la journée",
  "apres-diplome": "Après le diplôme",
};

/* ---------- Tableau « ce que je peux encadrer » ---------- */

/*
 * Les types de sortie ne sont volontairement pas typés par Univers :
 * « Bivouac » ou « Itinérance en raquettes » n'en sont pas un.
 */
export interface LigneEncadrement {
  sortie: string;
  modalite: Modalite;
}

/** L'ordre du tableau est l'ordre d'affichage : du « oui » vers « après le diplôme ». */
export const ENCADREMENT: LigneEncadrement[] = [
  { sortie: "Randonnée, demi-journée ou journée", modalite: "autonomie" },
  { sortie: "Itinérance en refuge ou gîte gardé", modalite: "autonomie" },
  { sortie: "Raquettes", modalite: "binome" },
  { sortie: "Bivouac sous tente", modalite: "apres-diplome" },
  { sortie: "Itinérance en raquettes", modalite: "apres-diplome" },
];

/* ---------- Garanties (bloc « Qui vous encadre ») ---------- */

export interface Garantie {
  titre: string;
  texte: string;
  /** Version courte du texte, pour les affichages compacts (accueil). */
  court: string;
  /** Pictogramme : attribut `d` d'un <path> SVG 24×24 en trait. */
  icone: string;
}

export const GARANTIES: Garantie[] = [
  {
    titre: "En formation au DE",
    court: "Statut vérifiable auprès du ministère des Sports",
    texte:
      "Educateur sportif stagiaire, mon statut est vérifiable sur le site du ministère des sports.",
    // toque de diplômé
    icone: "M2 8l10-5 10 5-10 5zM6 10v5c3 2.5 9 2.5 12 0v-5",
  },
  {
    titre: "Sous convention de stage",
    court: "Suivi par un conseiller de stage diplômé",
    texte:
      "J'encadre dans le cadre de ma convention, suivi par un conseiller de stage diplômé.",
    // document validé
    icone: "M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 14l3 3 5-6",
  },
  {
    titre: "Assuré",
    court: "Responsabilité civile professionnelle",
    texte:
      "Responsabilité civile professionnelle d'accompagnateur stagiaire [TODO: assureur à completer].",
    // bouclier
    icone: "M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z",
  },
];

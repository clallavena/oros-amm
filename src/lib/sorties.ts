/**
 * Accès aux données de la collection « sorties ».
 * Les pages passent par ces fonctions plutôt que d'appeler getCollection
 * directement : le filtrage (brouillons) et le tri sont écrits une seule fois.
 */
import { getCollection, type CollectionEntry } from "astro:content";
import { UNIVERS, type Univers } from "./univers";
import { FORMATS, type Format } from "./formats";
import { THEMATIQUES, type Thematique } from "./thematiques";

export type Sortie = CollectionEntry<"sorties">;

/**
 * Sorties publiées, triées par `ordre` puis par prix croissant.
 * @param univers si fourni, ne garde que les sorties de cet univers.
 */
export async function getSorties(univers?: Univers): Promise<Sortie[]> {
  const sorties = await getCollection(
    "sorties",
    ({ data }) =>
      !data.brouillon && (univers === undefined || data.univers === univers),
  );

  return sorties.sort(
    (a, b) => a.data.ordre - b.data.ordre || a.data.prix.des - b.data.prix.des,
  );
}

/**
 * Thématiques qu'une sortie permet d'aborder.
 * Une sortie sur mesure se construit autour de l'envie du client : elle les
 * aborde toutes, sans qu'il faille les recopier dans son frontmatter (et une
 * thématique ajoutée plus tard dans THEMATIQUES y sera incluse d'office).
 */
export const thematiquesAbordees = (sortie: Sortie): Thematique[] =>
  sortie.data.format === "sur-mesure" ? [...THEMATIQUES] : sortie.data.thematiques;

/** URL de la fiche : /sorties/<univers>/<nom-du-fichier> */
export const sortieHref = (sortie: Sortie): string =>
  `/sorties/${sortie.data.univers}/${sortie.id}`;

/** Ce qu'on peut dire d'un ensemble de sorties (un univers, un format…). */
export interface ResumeSorties {
  nombre: number;
  /** Formats présents, dans l'ordre de FORMATS. */
  formats: Format[];
  /** Univers présents, dans l'ordre de UNIVERS. */
  univers: Univers[];
  /** Plus petit prix « dès » ; undefined s'il n'y a aucune sortie. */
  prixDes?: number;
  /** Thématiques abordées, dans l'ordre de THEMATIQUES. */
  thematiques: Thematique[];
}

/**
 * Résume un ensemble de sorties à partir du contenu publié.
 * Les cartes d'univers et le comparatif des formats affichent donc toujours
 * des informations vraies : ajouter un .md met le hub à jour tout seul.
 */
export function resumer(sorties: Sortie[]): ResumeSorties {
  return {
    nombre: sorties.length,
    formats: FORMATS.filter((f) => sorties.some((s) => s.data.format === f)),
    univers: UNIVERS.filter((u) => sorties.some((s) => s.data.univers === u)),
    prixDes:
      sorties.length > 0
        ? Math.min(...sorties.map((s) => s.data.prix.des))
        : undefined,
    // Via thematiquesAbordees : une sortie sur mesure apporte toutes les thématiques.
    thematiques: THEMATIQUES.filter((t) => sorties.some((s) => thematiquesAbordees(s).includes(t))),
  };
}

/**
 * Renvoie les sorties les plus proches de la sortie donnée. Dans le même univers, triées par ordre puis prix croissant.
 * @param sortie La sortie de référence pour trouver les sorties proches.
 * @param max Le nombre maximum de sorties proches à renvoyer.
 * @returns Au plus `max` sorties du même univers, hors la sortie elle-même ; [] s’il n’y en a pas.
 */
export async function getSortiesProches(sortie: Sortie, max = 2): Promise<Sortie[]> {
  const sorties = await getSorties(sortie.data.univers);
  return sorties
    .filter((s) => s.id !== sortie.id)
    .slice(0, max);
}

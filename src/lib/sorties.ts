/**
 * Accès aux données de la collection « sorties ».
 * Les pages passent par ces fonctions plutôt que d'appeler getCollection
 * directement : le filtrage (brouillons) et le tri sont écrits une seule fois.
 */
import { getCollection, type CollectionEntry } from "astro:content";
import { UNIVERS, type Univers } from "./univers";
import { FORMATS, type Format } from "./formats";

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
  /** Thèmes abordés, sans doublon. */
  themes: string[];
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
    themes: [...new Set(sorties.flatMap((s) => s.data.themes))],
  };
}

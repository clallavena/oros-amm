/**
 * Accès aux données de la collection « sorties ».
 * Les pages passent par ces fonctions plutôt que d'appeler getCollection
 * directement : le filtrage (brouillons) et le tri sont écrits une seule fois.
 */
import { getCollection, type CollectionEntry } from "astro:content";
import type { Univers } from "./univers";

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

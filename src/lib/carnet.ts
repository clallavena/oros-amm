/**
 * Accès aux récits du Carnet, triés du plus récent au plus ancien.
 * Même principe que lib/sorties.ts : le tri est écrit une seule fois.
 */
import { getCollection, type CollectionEntry } from "astro:content";
import type { Univers } from "./univers";

export type Recit = CollectionEntry<"carnet">;

/**
 * @param options.univers si fourni, ne garde que les récits rattachés à cet univers.
 * @param options.limite nombre maximal de récits renvoyés.
 */
export async function getRecits(
  options: { univers?: Univers; limite?: number } = {},
): Promise<Recit[]> {
  const { univers, limite } = options;
  const recits = await getCollection(
    "carnet",
    ({ data }) => univers === undefined || data.univers === univers,
  );
  recits.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return limite === undefined ? recits : recits.slice(0, limite);
}

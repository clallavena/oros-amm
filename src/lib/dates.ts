/**
 * Date longue en français : « 12 mars 2026 ».
 * Fuseau fixé à Paris : le résultat ne dépend pas du fuseau de la machine de build.
 */
export const formatDate = (date: Date): string =>
  date.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "Europe/Paris",
  });

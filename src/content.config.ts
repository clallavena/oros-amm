import { defineCollection } from "astro:content";
// Depuis Astro 6, `z` s'importe depuis astro/zod (l'export de astro:content est déprécié).
import { z } from "astro/zod";
import { glob } from "astro/loaders";

import { UNIVERS } from "./lib/univers";
import { FORMATS, NIVEAUX } from "./lib/formats";
import { THEMATIQUES } from "./lib/thematiques";

/* Carnet (ex-blog) : récits et conseils. Dossier : src/content/carnet/ */
const carnet = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/carnet" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
  }),
});

/*
 * Une sortie = un fichier .md dans src/content/sorties/.
 * Le nom du fichier devient l'identifiant et la fin de l'URL :
 * balade-decouverte.md → /sorties/<univers>/balade-decouverte
 *
 * Frontmatter : tout ce qui s'affiche dans un bloc structuré
 * (chiffres clés, prix, programme…).
 * Corps du Markdown : le texte libre de la fiche (« L'idée »).
 */
const sorties = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/sorties" }),

  // Le schéma est une fonction pour recevoir le helper `image()` :
  // les chemins d'images sont vérifiés au build et optimisés par <Image />.
  schema: ({ image }) => {
    const photo = z.object({
      src: image(),
      // Obligatoire : une image sans texte alternatif ne respecte pas WCAG 1.1.1.
      alt: z.string().min(1, { error: "Texte alternatif obligatoire" }),
    });

    return z.object({
      title: z.string(),
      /** Résumé court : cartes et balise meta description. */
      description: z.string(),

      univers: z.enum(UNIVERS),
      format: z.enum(FORMATS),
      niveau: z.enum(NIVEAUX),

      lieu: z
        .object({
          massif: z.string(),
          depart: z.string().optional(),
        })
        .optional(),

      // Chiffres clés : tous optionnels, une sortie sur mesure n'a pas de dénivelé fixe.
      // Durées en texte libre : « 2 j · 1 nuit », « 4 à 5 h »… s'affichent telles quelles.
      duree: z.string().optional(),
      marcheParJour: z.string().optional(),
      distanceKm: z.number().positive().optional(),
      deniveleM: z.number().int().nonnegative().optional(),
      altitudeMaxM: z.number().int().positive().optional(),

      groupe: z
        .object({
          min: z.number().int().positive(),
          max: z.number().int().positive().optional(),
        })
        .refine((g) => g.max === undefined || g.min <= g.max, {
          error: "groupe.min doit être inférieur ou égal à groupe.max",
        }),

      prix: z
        .object({
          /** Prix « dès », par personne. */
          des: z.number().positive(),
          jusqua: z.number().positive().optional(),
        })
        .refine((p) => p.jusqua === undefined || p.des <= p.jusqua, {
          error: "prix.des doit être inférieur ou égal à prix.jusqua",
        }),

      /**
       * Thématiques de découverte (lib/thematiques.ts) : faune, flore,
       * milieu, vie-en-montagne. Servent au filtre de la page d'univers.
       * Une valeur inconnue fait échouer le build.
       */
      thematiques: z.array(z.enum(THEMATIQUES)).default([]),

      couverture: photo,
      galerie: z.array(photo).default([]),

      programme: z
        .array(
          z.object({
            moment: z.string(), // « Jour 1 », « Soir »…
            heure: z.string().optional(), // « 9 h »
            texte: z.string(),
          }),
        )
        .default([]),

      inclus: z.array(z.string()).default([]),

      /* ---------- Lot 5 : fiche complète ---------- */

      /**
       * true = itinéraire type, adaptable selon la météo et le groupe.
       * Affiche le badge « Sortie type » et l'encadré d'explication.
       */
      itineraireType: z.boolean().default(false),

      /**
       * Le niveau en termes concrets, affiché dans « Le terrain »
       * après « Niveau : modéré. » (commence donc par une majuscule).
       * Ex. : « Vous marchez régulièrement et tenez 4 à 5 h de marche
       * avec un sac de 6 à 8 kg. Pas de passage technique ni de vide. »
       */
      niveauDetail: z.string().optional(),

      /**
       * Dates programmées. Format AAAA-MM-JJ dans le frontmatter.
       * Seules les dates à venir s'affichent (calculé au moment du build).
       */
      departs: z
        .array(
          z
            .object({
              debut: z.coerce.date(),
              fin: z.coerce.date().optional(),
              /** Places restantes ; 0 = complet ; absent = non affiché. */
              places: z.number().int().nonnegative().optional(),
            })
            .refine((d) => d.fin === undefined || d.fin >= d.debut, {
              error: "departs.fin doit être postérieure ou égale à departs.debut",
            }),
        )
        .default([]),

      /** Conditions d'annulation, en une phrase. */
      annulation: z.string().optional(),

      /** Ordre d'affichage dans les listes (petit = en premier). */
      ordre: z.number().int().default(0),
      /** true = la sortie n'est pas publiée. */
      brouillon: z.boolean().default(false),
    });
  },
});

export const collections = { carnet, sorties };

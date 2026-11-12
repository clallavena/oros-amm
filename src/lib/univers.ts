/**
 * Deux notions distinctes, à ne pas confondre :
 *
 * - le THÈME : l'ambiance visuelle (couleurs). Il s'applique à n'importe
 *   quelle page via <BaseLayout theme="…">.
 * - l'UNIVERS : une catégorie de sorties, qui apparaît dans les URL
 *   (/sorties/randonnee/…). Chaque univers a UN thème.
 *
 * « forest » est à la fois le thème de la marque (accueil, groupes…)
 * et celui de l'univers Randonnée : c'est pour ça qu'on ne fusionne pas
 * les deux notions.
 */

/* ---------- Thèmes ---------- */
import photoRandonnee from "../images/forest_montblanc.jpg";
import sunsetImage from "../images/sunset2.jpg";
import snowImage from "../images/raquette.jpg";

export const THEMES = ["forest", "snow", "sunset"] as const;

export interface HeroPhoto {
  image: ImageMetadata,
  alt: string,
};

/* Images HERO pour les univers */
export const PHOTOS: Record<Univers, HeroPhoto> = {
  randonnee: { image: photoRandonnee, alt: "Randonnée sur un sentier de montagne" },
  hiver: { image: snowImage, alt: "Randonnée raquette sur un sentier enneigé"},
  itinerance: { image: sunsetImage, alt: "Ligne d'horizon au crépuscule" },
};

export type Theme = (typeof THEMES)[number];

/**
 * Couleur de la barre du navigateur mobile pour chaque thème.
 * Valeurs = la couleur `primary` du thème (voir global.css).
 */
export const THEME_COLOR: Record<Theme, string> = {
  forest: "#295943",
  snow: "#23517a",
  sunset: "#753061",
};

/* ---------- Univers ---------- */

/** Utilisé tel quel dans les URL : ne pas mettre d'accents ni d'espaces. */
export const UNIVERS = ["randonnee", "hiver", "itinerance"] as const;

export type Univers = (typeof UNIVERS)[number];

export interface UniversInfo {
  label: string;
  /** Libellé court pour les tableaux : « Rando », « Hiver »… */
  labelCourt: string;
  theme: Theme;
  /** Petite ligne au-dessus du titre sur la carte d'univers. */
  surtitre: string;
  /** Phrase d'accroche (textes du design, planche « Hub Sorties »). */
  accroche: string;
  /** Texte du bouton qui mène à la page de l'univers. */
  cta: string;
  /** Pictogramme : attribut `d` d'un <path> SVG 24×24 en trait (design). */
  icone: string;
  /** Textes de la page /sorties/<univers> (design, planches 2 à 4). */
  page: {
    /** Phrase d'accroche du hero, sous le nom de l'univers. */
    titre: string;
    intro: string;
    /**
     * Pastilles « En bref » propres à l'univers. Les formats et le prix
     * « dès » sont ajoutés automatiquement depuis le contenu publié.
     */
    enBref: string[];
    /** Titre de la section des formules. */
    formules: string;
    /** Titre de l'appel à l'action en bas de page. */
    appel: string;
    /** Titre de la section des récits du Carnet liés à l'univers. */
    recits: string;
    /**
     * « Inclus » et « À prévoir » communs aux sorties de l'univers.
     * La section n'apparaît que si au moins une des deux listes est renseignée.
     * Chaque fiche garde son propre `inclus` pour le détail.
     */
    inclus?: string[];
    aPrevoir?: string[];
    /**
     * Encart « Bientôt » : une pratique de l'univers que le statut de
     * stagiaire ne permet pas encore d'encadrer (voir ENCADREMENT dans
     * statut.ts). Le bouton mène à /contact?sortie=<id>, où une option
     * « Être prévenu » est pré-sélectionnée.
     */
    bientot?: {
      /** Valeur envoyée par le formulaire de contact : sans accents ni espaces. */
      id: string;
      titre: string;
      texte: string;
    };
  };
}

/*
 * Record<Univers, …> : TypeScript refuse de compiler si un univers
 * de la liste n'a pas son entrée ici (même idée qu'un switch exhaustif).
 */
export const UNIVERS_INFO: Record<Univers, UniversInfo> = {
  randonnee: {
    label: "Randonnée & découverte",
    labelCourt: "Rando",
    theme: "forest",
    surtitre: "Sentiers & natures",
    accroche:
      "Marcher pour comprendre : faune, flore, paysages et vie du milieu montagnard.",
    cta: "Voir les sorties rando",
    page: {
      titre: "Marcher pour comprendre la montagne.",
      intro:
        "Une trace dans la boue, une fleur qu'on ne remarquait pas, un alpage qui raconte une histoire : ici, la marche sert à observer.",
      enBref: ["Tous niveaux"],
      formules: "Une balade ou une vraie journée d'immersion",
      appel: "Et si on partait observer ?",
      recits: "Récits de randonnée",
    },
    icone: "M12 22v-3M17 14 l3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 9h-.2A1 1 0 0 1 8 7.3L12 3l4 4.3a1 1 0 0 1-.8 1.7H15l3 3.3a1 1 0 0 1-.7 1.7H17Z", // sapin
  },
  hiver: {
    label: "Hiver & raquettes",
    labelCourt: "Hiver",
    theme: "snow",
    surtitre: "Neige & raquettes",
    accroche:
      "Forêts enneigées, traces d'animaux et silence feutré : la montagne se découvre autrement l'hiver.",
    cta: "Voir les sorties hiver",
    page: {
      titre: "La montagne en silence.",
      intro:
        "Des sorties en raquettes pour marcher dans la poudreuse, lire les traces d'animaux et profiter de l'hiver sans savoir skier.",
      enBref: ["Selon l'enneigement", "En binôme avec un accompagnateur diplômé"],
      formules: "Une matinée ou une journée dans la neige",
      appel: "Envie de marcher dans la neige ?",
      recits: "Récits d'hiver",
    },
    icone: "M12 2V18M12 22V18M12 18L15 21M12 18L9 21M15 3L12 6L9 3M3.34 7L6.8 9M6.8 9L17.2 15M6.8 9L5.71 4.9M6.8 9L2.71 10.1M17.2 15L20.66 17M17.2 15L21.29 13.9M17.2 15L18.29 19.1M20.66 7L17.2 9M17.2 9L6.8 15M17.2 9L18.29 4.9M17.2 9L21.29 10.1M6.8 15L3.34 17M6.8 15L2.71 13.9M6.8 15L5.71 19.1", // flocon (svg repo)
  },
  itinerance: {
    label: "Itinérance & refuges",
    labelCourt: "Itinérance",
    theme: "sunset",
    surtitre: "Nuits en refuge",
    accroche:
      "Plusieurs jours de marche, de refuge en refuge, et le lever du jour là-haut.",
    cta: "Voir les itinérances",
    page: {
      titre: "Passer la nuit là-haut.",
      intro:
        "Monter quand la foule redescend, poser le sac au refuge, regarder la lumière changer sur les sommets. Puis repartir au matin, plus loin.",
      enBref: ["Refuges et gîtes gardés"],
      formules: "Une nuit pour découvrir, plusieurs jours pour voyager",
      appel: "Prêt à dormir là-haut ?",
      recits: "Récits d'itinérance",
      // TODO : confirmer ce qui est inclus (réservation, demi-pension…).
      inclus: [
        "Encadrement par un accompagnateur en montagne stagiaire, sous convention de stage",
        "Préparation de l'itinéraire et suivi météo",
        "[À confirmer : réservation des refuges]",
        "[À confirmer : demi-pension au refuge]",
      ],
      aPrevoir: [
        "Sac à dos de [30 à 40 L] et drap-sac pour le refuge",
        "Chaussures de randonnée déjà portées",
        "Vêtements chauds pour le soir, même en été",
      ],
      bientot: {
        id: "bientot-bivouac",
        titre: "Le bivouac sous tente",
        texte:
          "Je le proposerai une fois mon diplôme obtenu : pendant la formation, les nuits en bivouac ne font pas partie de mes prérogatives. Écrivez-moi, je vous préviendrai.",
      },
    },
    icone: "m14 10 3-3 3 3M14 5 l3-3 3 3 M17 14H7l-5 8h20Z M17 14V2 M8 14v8 M9 14 l5 8 M2 4 a2 2 0 1 0 4 0 a2 2 0 1 0 -4 0", // tente / refuge
  },
};

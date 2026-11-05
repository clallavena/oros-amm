/**
 * Réglages du site, regroupés ici pour être changés à un seul endroit.
 */

export const CONTACT_EMAIL = "allavenaclementcg@gmail.com";
export const PHONE_NUMBER = "06 01 46 54 13";

/**
 * Adresse d'envoi du formulaire de contact (service Formspree).
 *
 * Pour l'activer :
 * 1. crée un compte sur formspree.io et un nouveau formulaire ;
 * 2. copie son adresse, de la forme https://formspree.io/f/xxxxxxxx ;
 * 3. remplace null par cette adresse (entre guillemets).
 *
 * Tant que la valeur est null, le formulaire s'affiche mais le bouton d'envoi
 * est désactivé, avec un message qui invite à écrire directement par e-mail.
 * Pour changer de service plus tard, c'est la seule ligne à modifier
 * (et la mention RGPD sous le formulaire, qui nomme le service).
 */
export const CONTACT_FORM_ENDPOINT: string | null = null;

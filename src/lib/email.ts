import { BREVO_API_KEY } from "astro:env/server";
import { CONTACT_EMAIL } from "./site";

/** Ce que le visiteur a saisi : les champs validés par l'Action. */
export interface DemandeContact {
  nom: string;
  email: string;
  message: string;
  sortie: string;
  telephone?: string | null;
  personnes?: number | null;
  dates?: string | null;
}

/** Expéditeur : doit être déclaré et vérifié dans Brevo. */
const EXPEDITEUR = { name: "Site Oros", email: CONTACT_EMAIL };

export async function envoyerEmailContact(demande: DemandeContact): Promise<void> {
  // Une ligne par information ; les champs vides (null) sont retirés,
  // comme dans SortieCardCompacte.
  const lignes: [string, string | number | null | undefined][] = [
    ["Nom", demande.nom],
    ["E-mail", demande.email],
    ["Téléphone", demande.telephone],
    ["Nombre de personnes", demande.personnes],
    ["Dates souhaitées", demande.dates],
    ["Demande concernant", demande.sortie],
  ];

  const texte = [
    ...lignes
      .filter(([, valeur]) => valeur !== null && valeur !== undefined)
      .map(([libelle, valeur]) => `${libelle} : ${valeur}`),
    "",
    "Message :",
    demande.message,
  ].join("\n");

  const reponse = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: {
      "api-key": BREVO_API_KEY,
      "content-type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify({
      sender: EXPEDITEUR,
      to: [{ email: CONTACT_EMAIL }],
      replyTo: { email: demande.email },
      subject: `Demande de contact : ${demande.nom.replace(/\s+/g, " ")}`,
      textContent: texte,
    }),
    // Si Brevo ne répond pas en 10 s, on abandonne au lieu de bloquer le visiteur.
    signal: AbortSignal.timeout(10_000),
  });

  if (!reponse.ok) {
    // Ce détail ne s'affiche que dans le terminal du serveur, jamais au visiteur.
    const detail = await reponse.text().catch(() => "");
    throw new Error(`Brevo a refusé l'envoi (${reponse.status}) : ${detail}`);
  }
}
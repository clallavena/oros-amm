import { defineAction } from "astro:actions";
import { z } from "astro/zod";
import { envoyerEmailContact } from "../lib/email";

export const server = {
    contact: defineAction({
        accept: "form",
        input: z.object({
            nom: z.string("Le nom est obligatoire").trim().min(1, "Le nom est obligatoire").max(100, "Le nom ne peut pas dépasser 100 caractères"),
            email: z.email("Saissir une adresse email valide").max(100, "L'adresse email ne peut pas dépasser 100 caractères"),
            message: z.string("Le message est obligatoire").trim().min(1, "Le message est obligatoire").max(5000, "Le message ne peut pas dépasser 5000 caractères"),
            telephone: z.string().max(50).nullish(),
            personnes: z.number().int().positive().nullish(),
            dates: z.string().max(100).nullish(),
            sortie: z.string().max(50),
            honeypot: z.string().nullish(),
        }),
        handler: async (input) => {
            if (input.honeypot) {
                // Le champ honeypot est rempli : c'est un robot. On ne fait rien.
                return { ok: true };
            }
            await envoyerEmailContact(input);
            return { ok: true };
        },
    }),
};
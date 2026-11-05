// @ts-check
import { defineConfig, envField, fontProviders } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import react from '@astrojs/react';

import node from "@astrojs/node";

// https://astro.build/config
export default defineConfig({
  fonts: [{
    provider: fontProviders.fontsource(),
    name: "Epilogue",
    cssVariable: "--font-epilogue",
    weights: ["600 700"],
    styles: ["normal"],
    fallbacks: ["sans-serif"],
  }, {
    provider: fontProviders.fontsource(),
    name: "Inter",
    cssVariable: "--font-inter",
    weights: ["400 700"],
    styles: ["normal", "italic"],
    fallbacks: ["sans-serif"],
  }],
  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [react()],

  adapter: node({
    mode: "standalone"
  }),
  env: {
    schema: {
      BREVO_API_KEY: envField.string({context: "server", access: "secret"}),
    },
  },
});
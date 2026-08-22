// @ts-check
import { defineConfig, fontProviders } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  fonts: [{
    provider: fontProviders.fontsource(),
    name: "Epilogue",
    cssVariable: "--font-epilogue",
  }, {
    provider: fontProviders.fontsource(),
    name: "Inter",
    cssVariable: "--font-inter",
  }],
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [react()]
});
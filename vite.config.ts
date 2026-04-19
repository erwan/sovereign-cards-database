import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type Plugin } from 'vite';
import sharp from 'sharp';
import {
  readdirSync, mkdirSync, existsSync, statSync,
  readFileSync, writeFileSync, copyFileSync,
} from 'fs';
import { join } from 'path';

const DIST_CARDS = 'dist/cards';
const SRC_CARDS = 'static/cards';
const CACHE_DIR = '.svelte-kit/optimized-images';
const JPEG_QUALITY = 75;
const CONFIG_VERSION = `mozjpeg-q${JPEG_QUALITY}`;

function optimizeCardImagesPlugin(): Plugin {
  return {
    name: 'optimize-card-images',
    enforce: 'post',
    apply: 'build',
    async closeBundle() {
      if (!existsSync(DIST_CARDS)) return;

      const factions = readdirSync(DIST_CARDS, { withFileTypes: true })
        .filter((d) => d.isDirectory())
        .map((d) => d.name);

      await Promise.all(
        factions.map(async (faction) => {
          const distFactionDir = join(DIST_CARDS, faction);
          const srcFactionDir = join(SRC_CARDS, faction);
          const cacheDir = join(CACHE_DIR, faction);
          if (!existsSync(cacheDir)) mkdirSync(cacheDir, { recursive: true });

          const versionFile = join(cacheDir, '.version');
          const cachedVersion = existsSync(versionFile) ? readFileSync(versionFile, 'utf8') : '';
          const configChanged = cachedVersion !== CONFIG_VERSION;

          const files = readdirSync(distFactionDir).filter((f) => f.endsWith('.jpg'));

          await Promise.all(
            files.map(async (file) => {
              const srcPath = join(srcFactionDir, file);
              const distPath = join(distFactionDir, file);
              const cachePath = join(cacheDir, file);

              if (!configChanged && existsSync(cachePath)) {
                const srcMtime = statSync(srcPath).mtimeMs;
                const cacheMtime = statSync(cachePath).mtimeMs;
                if (cacheMtime >= srcMtime) {
                  copyFileSync(cachePath, distPath);
                  return;
                }
              }

              await sharp(srcPath)
                .jpeg({ quality: JPEG_QUALITY, mozjpeg: true })
                .toFile(distPath);

              copyFileSync(distPath, cachePath);
            })
          );

          writeFileSync(versionFile, CONFIG_VERSION);
        })
      );
    },
  };
}

export default defineConfig({
  plugins: [sveltekit(), optimizeCardImagesPlugin()],
});

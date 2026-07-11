/* ==========================================================================
   Swiss NCC — scarica le immagini remote e rende il sito autonomo
   --------------------------------------------------------------------------
   Da eseguire in LOCALE (dove la rete non e' bloccata), dentro la cartella
   sito-ncc:
       node scarica-immagini.mjs
   Scarica le foto panoramiche in ./img e aggiorna i riferimenti nelle pagine
   HTML, cosi' il sito funziona anche offline / senza dipendere dai server
   esterni del cliente.
   ========================================================================== */
import fs from 'fs';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const imgDir = path.join(here, 'img');
fs.mkdirSync(imgDir, { recursive: true });

// URL remoto (come appare nell'HTML)  ->  file locale di destinazione
const MAP = {
  'https://ik.imagekit.io/swissncc/assets/media/blogs/SwissNCC-blog-3.png?tr=w-1920,q-90': 'img/about-berlina.png',
  'https://ik.imagekit.io/swissncc/assets/media/blogs/SwissNCC-blog-1.png?tr=w-1920,q-90': 'img/storia-strada.png',
  'https://ik.imagekit.io/swissncc/assets/media/cars/SwissNCC-Zermatt.jpg?tr=w-1920,q-90': 'img/zermatt.jpg',
  'https://ik.imagekit.io/swissncc/assets/media/cars/SwissNCC-Davos-Platz.jpg?tr=w-1920,q-90': 'img/davos.jpg',
  'https://d8j0ntlcm91z4.cloudfront.net/user_3EDw5qmardIfuEPJwyYr4uyUEvi/hf_20260711_002155_e549d135-5f70-4db5-8310-94480bbd1f6b.png': 'img/servizi-alpi.png',
  'https://d8j0ntlcm91z4.cloudfront.net/user_3EDw5qmardIfuEPJwyYr4uyUEvi/hf_20260704_201130_b3150070-5395-4919-871d-0f6d706860ff.png': 'img/team-flotta.png',
};

const pages = ['index.html', 'servizi.html', 'chi-siamo.html', 'team.html', 'contatti.html', 'prenota.html'];

async function download(url, dest) {
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(path.join(here, dest), buf);
  return buf.length;
}

let ok = 0;
for (const [url, dest] of Object.entries(MAP)) {
  try {
    const bytes = await download(url, dest);
    console.log(`✔  ${dest}  (${Math.round(bytes / 1024)} KB)`);
    ok++;
  } catch (e) {
    console.log(`✖  ${dest}  — errore: ${e.message}`);
  }
}

// aggiorna i riferimenti nelle pagine HTML
for (const p of pages) {
  const fp = path.join(here, p);
  if (!fs.existsSync(fp)) continue;
  let html = fs.readFileSync(fp, 'utf8');
  let changed = false;
  for (const [url, dest] of Object.entries(MAP)) {
    if (html.includes(url)) { html = html.split(url).join(dest); changed = true; }
  }
  if (changed) { fs.writeFileSync(fp, html); console.log(`↺  aggiornato ${p}`); }
}

console.log(`\nFatto: ${ok}/${Object.keys(MAP).length} immagini scaricate in ./img`);
console.log('Ora il sito e\' autonomo. Ricordati di fare commit + push.');

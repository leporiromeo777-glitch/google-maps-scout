# Swiss NCC — Sito web (redesign 2026)

Sito statico rigenerato da zero: più ordinato, moderno e intuitivo rispetto alla
versione precedente. Tema chiaro, font Inter, card arrotondate, icone al posto
dei numeri romani, CSS e JS condivisi.

## Struttura
- `index.html` — home (hero, prenotazione rapida, servizi, flotta, tratte, come funziona, recensioni, FAQ)
- `servizi.html` — dettaglio servizi + flotta + come funziona
- `chi-siamo.html` — storia, timeline, missione/visione/valori
- `team.html` — fondatore, competenze, numeri
- `contatti.html` — canali di contatto + info prenotazione
- `prenota.html` — wizard di prenotazione in 4 passi (invio via WhatsApp)
- `styles.css` — design system condiviso
- `script.js` — menu mobile, reveal on scroll, FAQ, prenotazione rapida, wizard
- `*.webp` — logo e immagini della flotta

## Note
- Tutto client-side, nessuna dipendenza da build.
- Il font Inter è caricato da Google Fonts (fallback a font di sistema).
- Alcune immagini scenografiche (montagne/città) sono servite dalla CDN del cliente
  (imagekit / cloudfront); le immagini della flotta e il logo sono locali.
- Il wizard di prenotazione compone un messaggio riepilogativo e apre WhatsApp
  (numero `+41 76 75 65 725`).

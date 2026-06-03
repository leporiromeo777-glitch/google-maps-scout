# Google Maps Scout — Ticino

## Cosa fa
Cerca nuovi lead in Ticino via Google Maps Places API, evita duplicati, seleziona i 10 con qualità web peggiore e genera HTML + JSON injection.

## Struttura
- `execution/main.py` — script principale
- `memory/businesses_seen.json` — place_id già visti (aggiornato ad ogni run)
- `output/leads_YYYY-MM-DD.html` — report HTML giornaliero
- `output/latest.json` — JSON injection per il tab "Clienti senza sito" (sovrascritto ad ogni run)
- `.github/workflows/scout.yml` — automazione giornaliera (09:00 ora svizzera)

## Credenziali
- **GOOGLE_MAPS_API_KEY** → GitHub Actions Secret (già configurata)
- **GitHub PAT** → variabile d'ambiente `$GITHUB_PAT` (già in settings.local.json)
- **Repo** → `leporiromeo777-glitch/google-maps-scout`

## Prompt da usare in Claude Code

```
Esegui la routine Google Maps Scout:
1. Triggera il workflow GitHub Actions su leporiromeo777-glitch/google-maps-scout (usa $GITHUB_PAT)
2. Aspetta il completamento con polling ogni 10s (timeout 5 min)
3. Dimmi quanti lead sono stati trovati e i nomi dei file generati (HTML e latest.json)
```

## Output per ogni run
- Max 10 lead, ordinati per qualità sito peggiore (priorità: nessun sito > rating basso > poche recensioni)
- `output/leads_YYYY-MM-DD.html` — tabella navigabile con nome, città, settore, telefono, sito, rating
- `output/latest.json` — formato injection con campi: name, sector, city, address, phone, email, employees, description, subject, body

## Query di ricerca (modificabili in execution/main.py)
- ristorante Lugano / Bellinzona / Locarno
- parrucchiere Lugano
- estetista Ticino
- studio dentistico Ticino
- officina auto Ticino
- hotel Lugano / Locarno
- negozio abbigliamento Lugano

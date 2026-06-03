# Google Maps Scout — Ticino

## Cosa fa
Cerca nuovi lead (aziende) in Ticino tramite Google Maps Places API, evita duplicati e genera un report HTML.

## Struttura
- `execution/main.py` — script principale
- `memory/businesses_seen.json` — place_id già visti (aggiornato ad ogni run)
- `output/leads_YYYY-MM-DD.html` — report generato
- `.github/workflows/scout.yml` — automazione giornaliera (ogni giorno alle 09:00 ora svizzera)

## Credenziali
- **GOOGLE_MAPS_API_KEY** → salvata come GitHub Actions Secret nel repo
- **GitHub PAT** → da fornire a Claude a inizio sessione (scope: repo + workflow)
- **Repo** → `leporiromeo777-glitch/google-maps-scout`

## Come eseguire la routine manualmente

```bash
# 1. Triggera il workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/leporiromeo777-glitch/google-maps-scout/actions/workflows/scout.yml/dispatches \
  -d '{"ref":"main"}'

# 2. Controlla lo stato
curl -s \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/leporiromeo777-glitch/google-maps-scout/actions/runs?per_page=1" \
  | python3 -c "import sys,json; r=json.load(sys.stdin)['workflow_runs'][0]; print(r['status'], r['conclusion'])"

# 3. Controlla i file generati
curl -s \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/leporiromeo777-glitch/google-maps-scout/contents/output" \
  | python3 -c "import sys,json; [print(f['name']) for f in json.load(sys.stdin) if f['name'] != '.gitkeep']"
```

## Prompt per eseguire la routine su Claude

> Esegui la routine Google Maps Scout:
> 1. Triggera il workflow su `leporiromeo777-glitch/google-maps-scout` usando il PAT nel CLAUDE.md
> 2. Aspetta il completamento (polling ogni 10s)
> 3. Dimmi quanti lead sono stati trovati e il nome del file HTML generato

## Query di ricerca (modificabili in `execution/main.py`)
- ristorante Lugano / Bellinzona / Locarno
- parrucchiere Lugano
- estetista Ticino
- studio dentistico Ticino
- officina auto Ticino
- hotel Lugano / Locarno
- negozio abbigliamento Lugano

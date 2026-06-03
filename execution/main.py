import os
import json
import requests
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_env():
    env_path = BASE_DIR / ".env"
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def load_seen():
    path = BASE_DIR / "memory" / "businesses_seen.json"
    return set(json.loads(path.read_text()))

def save_seen(seen_set):
    path = BASE_DIR / "memory" / "businesses_seen.json"
    path.write_text(json.dumps(sorted(seen_set), indent=2))

def search_places(query, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    results = []
    params = {"query": query, "key": api_key}
    while True:
        r = requests.get(url, params=params, timeout=10).json()
        results.extend(r.get("results", []))
        token = r.get("next_page_token")
        if not token:
            break
        import time; time.sleep(2)
        params = {"pagetoken": token, "key": api_key}
    return results

def get_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    fields = "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,types"
    r = requests.get(url, params={"place_id": place_id, "fields": fields, "key": api_key}, timeout=10).json()
    return r.get("result", {})

QUERIES = [
    "ristorante Lugano",
    "ristorante Bellinzona",
    "ristorante Locarno",
    "parrucchiere Lugano",
    "estetista Ticino",
    "studio dentistico Ticino",
    "officina auto Ticino",
    "hotel Lugano",
    "hotel Locarno",
    "negozio abbigliamento Lugano",
]

def render_html(leads, today):
    rows = ""
    for b in leads:
        website = f'<a href="{b["website"]}" target="_blank">{b["website"]}</a>' if b.get("website") else "<em>—</em>"
        rows += f"""
        <tr>
          <td>{b.get('name','')}</td>
          <td>{b.get('address','')}</td>
          <td>{b.get('phone','') or '—'}</td>
          <td>{website}</td>
          <td>{b.get('rating','') or '—'} ({b.get('reviews','') or 0})</td>
          <td>{', '.join(b.get('types', [])[:2])}</td>
        </tr>"""
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Leads Ticino – {today}</title>
<style>
  body {{ font-family: sans-serif; padding: 2rem; background: #f8f9fa; }}
  h1 {{ color: #2c3e50; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
  th {{ background: #2c3e50; color: white; padding: .7rem 1rem; text-align: left; }}
  td {{ padding: .6rem 1rem; border-bottom: 1px solid #eee; font-size: .9rem; }}
  tr:hover td {{ background: #f0f4f8; }}
  .count {{ color: #7f8c8d; font-size: .95rem; margin-bottom: 1rem; }}
</style>
</head>
<body>
<h1>Leads Ticino – {today}</h1>
<p class="count">{len(leads)} nuovi lead trovati</p>
<table>
  <thead><tr>
    <th>Nome</th><th>Indirizzo</th><th>Telefono</th><th>Sito web</th><th>Rating</th><th>Categoria</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
</body>
</html>"""

def main():
    load_env()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise SystemExit("Imposta GOOGLE_MAPS_API_KEY nel file .env")

    seen = load_seen()
    new_leads = []
    new_ids = set()

    print(f"Place IDs già visti: {len(seen)}")

    for query in QUERIES:
        print(f"  Ricerca: {query}")
        places = search_places(query, api_key)
        for p in places:
            pid = p["place_id"]
            if pid in seen or pid in new_ids:
                continue
            details = get_details(pid, api_key)
            new_leads.append({
                "place_id": pid,
                "name": details.get("name", p.get("name", "")),
                "address": details.get("formatted_address", p.get("formatted_address", "")),
                "phone": details.get("formatted_phone_number", ""),
                "website": details.get("website", ""),
                "rating": details.get("rating", ""),
                "reviews": details.get("user_ratings_total", 0),
                "types": details.get("types", p.get("types", [])),
            })
            new_ids.add(pid)

    today = date.today().isoformat()
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    filename = f"leads_{today}.html"
    (output_dir / filename).write_text(render_html(new_leads, today))

    seen.update(new_ids)
    save_seen(seen)

    print(f"\nNuovi lead: {len(new_leads)}")
    print(f"File generato: output/{filename}")

if __name__ == "__main__":
    main()

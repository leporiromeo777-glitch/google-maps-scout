import os
import json
import requests
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAX_LEADS = 10

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

def website_quality_score(business):
    """Punteggio qualità sito: più basso = peggiore = priorità più alta."""
    if not business.get("website"):
        return 0   # nessun sito → peggiore
    rating = business.get("rating") or 0
    reviews = business.get("reviews") or 0
    # sito presente ma attività poco curata online
    if rating < 3.5 or reviews < 10:
        return 1
    if rating < 4.0 or reviews < 30:
        return 2
    return 3

def extract_city(address):
    if not address:
        return ""
    parts = address.split(",")
    for part in reversed(parts):
        part = part.strip()
        if any(city in part for city in ["Lugano", "Bellinzona", "Locarno", "Mendrisio",
                                          "Chiasso", "Ascona", "Muralto", "Giubiasco",
                                          "Cadenazzo", "Biasca", "Airolo"]):
            return part
    return parts[-2].strip() if len(parts) >= 2 else ""

def format_sector(types):
    mapping = {
        "restaurant": "Ristorante",
        "food": "Alimentare",
        "hair_care": "Parrucchiere",
        "beauty_salon": "Estetica",
        "dentist": "Studio dentistico",
        "car_repair": "Officina auto",
        "lodging": "Hotel / Alloggio",
        "clothing_store": "Negozio abbigliamento",
        "store": "Negozio",
        "health": "Salute",
        "gym": "Palestra",
        "spa": "Spa",
    }
    for t in types:
        if t in mapping:
            return mapping[t]
    return types[0].replace("_", " ").title() if types else "Attività locale"

def build_email(business):
    name = business.get("name", "")
    sector = format_sector(business.get("types", []))
    city = extract_city(business.get("address", ""))
    has_site = bool(business.get("website"))

    if not has_site:
        subject = f"Nuovi clienti online per {name} – Sito web professionale"
        body = (
            f"Buongiorno,\n\n"
            f"Ho notato che {name} a {city} non ha ancora un sito web. "
            f"Al giorno d'oggi la maggior parte dei clienti cerca online prima di scegliere un {sector.lower()}.\n\n"
            f"Posso crearvi un sito professionale, veloce e ottimizzato per Google in pochi giorni.\n\n"
            f"Sarebbe possibile sentirci per un preventivo gratuito?\n\n"
            f"Cordiali saluti"
        )
    else:
        subject = f"Miglioriamo la presenza online di {name}"
        body = (
            f"Buongiorno,\n\n"
            f"Ho visitato il sito di {name} e credo ci siano margini per migliorare "
            f"la visibilità su Google e aumentare le richieste di contatto.\n\n"
            f"Offro servizi di ottimizzazione SEO e restyling web per attività come la vostra.\n\n"
            f"Posso inviarvi un'analisi gratuita?\n\n"
            f"Cordiali saluti"
        )
    return subject, body

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
        website = f'<a href="{b["website"]}" target="_blank">{b["website"]}</a>' if b.get("website") else "<em>nessun sito</em>"
        rows += f"""
        <tr>
          <td>{b.get('name','')}</td>
          <td>{b.get('city','')}</td>
          <td>{b.get('sector','')}</td>
          <td>{b.get('phone','') or '—'}</td>
          <td>{website}</td>
          <td>{b.get('rating','') or '—'} ({b.get('reviews','') or 0})</td>
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
<p class="count">{len(leads)} lead selezionati (peggiore qualità web)</p>
<table>
  <thead><tr>
    <th>Nome</th><th>Città</th><th>Settore</th><th>Telefono</th><th>Sito web</th><th>Rating</th>
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
    all_leads = []
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
            types = details.get("types", p.get("types", []))
            address = details.get("formatted_address", p.get("formatted_address", ""))
            subject, body = build_email({
                "name": details.get("name", p.get("name", "")),
                "website": details.get("website", ""),
                "types": types,
                "address": address,
                "rating": details.get("rating", ""),
            })
            all_leads.append({
                "place_id": pid,
                "name": details.get("name", p.get("name", "")),
                "address": address,
                "city": extract_city(address),
                "phone": details.get("formatted_phone_number", ""),
                "website": details.get("website", ""),
                "rating": details.get("rating", ""),
                "reviews": details.get("user_ratings_total", 0),
                "types": types,
                "sector": format_sector(types),
                "subject": subject,
                "body": body,
            })
            new_ids.add(pid)

    # Ordina per qualità sito peggiore e limita a MAX_LEADS
    all_leads.sort(key=website_quality_score)
    leads = all_leads[:MAX_LEADS]

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    run_label = now.strftime("%d/%m/%Y")

    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    # HTML
    html_filename = f"leads_{today}.html"
    (output_dir / html_filename).write_text(render_html(leads, today))

    # JSON injection (sovrascrive sempre latest.json)
    injection = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M"),
        "run_label": run_label,
        "leads": [
            {
                "name": b["name"],
                "sector": b["sector"],
                "city": b["city"],
                "address": b["address"] or None,
                "phone": b["phone"] or None,
                "email": None,
                "employees": None,
                "description": f"{b['sector']} a {b['city']}. Rating: {b.get('rating') or 'N/D'} ({b.get('reviews') or 0} recensioni).",
                "subject": b["subject"],
                "body": b["body"],
            }
            for b in leads
        ],
    }
    json_content = json.dumps(injection, ensure_ascii=False, indent=2)
    (output_dir / "latest.json").write_text(json_content)

    # Copia in percorso Windows locale (solo se esiste il drive C:)
    import sys
    if sys.platform == "win32":
        win_dir = Path(r"C:\Users\romeo\agente claude\logs\injections\cerca_attivita_senza_sito")
        win_dir.mkdir(parents=True, exist_ok=True)
        (win_dir / "latest.json").write_text(json_content)
        print(f"JSON copiato in: {win_dir / 'latest.json'}")

    # Aggiorna seen solo con i lead effettivamente selezionati
    seen.update(new_ids)
    save_seen(seen)

    print(f"\nLead trovati totali: {len(all_leads)}")
    print(f"Lead selezionati (top {MAX_LEADS} peggiori): {len(leads)}")
    print(f"HTML: output/{html_filename}")
    print(f"JSON: output/latest.json")

if __name__ == "__main__":
    main()

"""
scripts/06_fetch_sofascore_squads.py
Obtiene números de camiseta y posiciones oficiales de Sofascore.

Requiere: pip install curl-cffi
Ejecutar:  python scripts/06_fetch_sofascore_squads.py
"""
import json, os, time, unicodedata, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "data", "processed")

# ── Importar curl-cffi (si no, intentar requests) ─────────────────────────────
try:
    from curl_cffi import requests as cffi_requests
    SESSION = cffi_requests.Session(impersonate="chrome124")
    print("✅ curl-cffi disponible — usando impersonation Chrome")
    def fetch(url):
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
except ImportError:
    print("⚠️  curl-cffi no instalado. Intentando con requests...")
    print("   Para mejor resultado: pip install curl-cffi")
    try:
        import requests
        SESSION = requests.Session()
        SESSION.headers.update({
            "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept":          "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer":         "https://www.sofascore.com/",
            "Origin":          "https://www.sofascore.com",
            "sec-ch-ua":       '"Chromium";v="124","Google Chrome";v="124","Not-A.Brand";v="99"',
            "sec-ch-ua-mobile":"?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest":  "empty",
            "sec-fetch-mode":  "cors",
            "sec-fetch-site":  "same-site",
            "DNT":             "1",
            "Connection":      "keep-alive",
        })
        # Pre-visit homepage to get Cloudflare cookies
        print("   Visitando sofascore.com para obtener cookies…")
        SESSION.get("https://www.sofascore.com/", timeout=15)
        time.sleep(2)
        def fetch(url):
            r = SESSION.get(url, timeout=15)
            r.raise_for_status()
            return r.json()
        print("   requests OK")
    except ImportError:
        print("❌ Ni curl-cffi ni requests disponibles.")
        print("   Instala: pip install curl-cffi")
        sys.exit(1)

# ── Normalización ─────────────────────────────────────────────────────────────
_SPECIAL = str.maketrans({
    'ø':'o','Ø':'o','ð':'d','Ð':'d','þ':'th','Þ':'th','ß':'ss',
    'æ':'ae','Æ':'ae','ł':'l','Ł':'l','đ':'d','Đ':'d','œ':'oe','Œ':'oe',
})
def norm(s):
    s = (s or '').translate(_SPECIAL)
    nfkd = unicodedata.normalize('NFD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn').lower().strip()

# ── Mapa splits-name → Sofascore team ID ──────────────────────────────────────
SOFASCORE_IDS = {
    # La Liga (tournament=8, season=77559)
    'FC Barcelona':              2817,
    'Real Madrid':               2829,
    'Villarreal CF':             2819,
    'Atlético de Madrid':        2836,
    'Real Betis':                2816,
    'Celta':                     2821,
    'Getafe CF':                 2859,
    'Rayo Vallecano':            2818,
    'Valencia CF':               2828,
    'Real Sociedad':             2824,
    'RCD Espanyol de Barcelona': 2814,
    'Athletic Club':             2825,
    'Sevilla FC':                2833,
    'Deportivo Alavés':          2885,
    'Elche CF':                  2846,
    'Levante UD':                2849,
    'CA Osasuna':                2820,
    'RCD Mallorca':              2826,
    'Girona FC':                 24264,
    'Real Oviedo':               2851,
    # Bundesliga (tournament=35, season=77333)
    'Bayern München':            2672,
    'Borussia Dortmund':         2673,
    'RB Leipzig':                36360,
    'VfB Stuttgart':             2677,
    'TSG Hoffenheim':            2569,
    'Bayer 04 Leverkusen':       2681,
    'SC Freiburg':               2538,
    'Eintracht Frankfurt':       2674,
    'FC Augsburg':               2600,
    '1. FSV Mainz 05':           2556,
    '1. FC Union Berlin':        2547,
    'Borussia Mönchengladbach':  2527,
    'Hamburger SV':              2676,
    '1. FC Köln':                2671,
    'Werder Bremen':             2534,
    'VfL Wolfsburg':             2524,
    'FC Heidenheim 1846':        5885,
    'FC St. Pauli':              2526,
    # Serie A (tournament=23, season=76457)
    'FC Internazionale':         2697,
    'SSC Napoli':                2714,
    'AS Roma':                   2702,
    'Como 1907':                 2704,
    'AC Milan':                  2692,
    'Juventus':                  2687,
    'Atalanta BC':               2686,
    'Bologna FC':                2685,
    'SS Lazio':                  2699,
    'Udinese Calcio':            2695,
    'US Sassuolo':               2793,
    'Parma Calcio':              2690,
    'Torino FC':                 2696,
    'Cagliari Calcio':           2719,
    'ACF Fiorentina':            2693,
    'Genoa CFC':                 2713,
    'US Lecce':                  2689,
    'US Cremonese':              2761,
    'Hellas Verona':             2701,
    'AC Pisa':                   2737,
    # Ligue 1 (tournament=34, season=77356)
    'Paris Saint-Germain':       1644,
    'RC Lens':                   1648,
    'LOSC Lille':                1643,
    'Olympique Lyonnais':        1649,
    'Olympique de Marseille':    1641,
    'Stade Rennais':             1658,
    'AS Monaco':                 1653,
    'RC Strasbourg':             1659,
    'FC Lorient':                1656,
    'Toulouse FC':               1681,
    'Paris FC':                  6070,
    'Stade Brestois 29':         1715,
    'Angers SCO':                1684,
    'Le Havre AC':               1662,
    'AJ Auxerre':                1646,
    'OGC Nice':                  1661,
    'FC Nantes':                 1647,
    'FC Metz':                   1651,
}

def sf_pos(pos_str):
    p = (pos_str or '').upper().strip()
    return p if p in ('G','D','M','F') else 'M'

def fetch_sofascore_team(team_id):
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/players"
    try:
        data = fetch(url)
    except Exception as e:
        print(f"ERROR: {e}")
        return {}
    result = {}
    for entry in data.get("players", []):
        player   = entry.get("player", {})
        name     = player.get("name", "")
        shirt    = entry.get("shirtNumber", 0) or 0
        pos      = sf_pos(player.get("position", ""))
        country_d = player.get("country", {}) or {}
        result[norm(name)] = {
            "shirt":    int(shirt),
            "position": pos,
            "country":  country_d.get("name", ""),
            "flag":     country_d.get("alpha2", ""),
            "sf_name":  name,
        }
    return result

def find_in_sf(player_name, sf_idx):
    n = norm(player_name)
    if n in sf_idx:
        return sf_idx[n]
    tokens = n.split()
    last = tokens[-1] if tokens else ''
    if len(last) >= 4:
        matches = [v for k, v in sf_idx.items() if k.endswith(' ' + last)]
        if len(matches) == 1:
            return matches[0]
    first = tokens[0] if tokens else ''
    if len(first) >= 4:
        matches = [v for k, v in sf_idx.items() if k.startswith(first + ' ') or k == first]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            valid = [m for m in matches if m['shirt'] > 0]
            if valid:
                return min(valid, key=lambda x: x['shirt'])
    return None

# ── Procesar ligas ────────────────────────────────────────────────────────────
LEAGUE_FILES = ['laliga', 'bundesliga', 'seriea', 'ligue1']

for league_key in LEAGUE_FILES:
    json_path = os.path.join(OUT, f"{league_key}_team_details.json")
    if not os.path.exists(json_path):
        print(f"Skipping {league_key} — JSON no encontrado")
        continue

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n{'='*50}")
    print(f"Actualizando {league_key.upper()}…")
    changed = 0

    for splits_name, team_data in data['teams'].items():
        sf_id = SOFASCORE_IDS.get(splits_name)
        if not sf_id:
            print(f"  {splits_name}: sin ID Sofascore")
            continue

        print(f"  {splits_name}…", end=" ", flush=True)
        sf_idx = fetch_sofascore_team(sf_id)
        time.sleep(0.6)

        if not sf_idx:
            print("sin datos")
            continue

        matched, unmatched = 0, 0
        for p in team_data['squad']:
            sf = find_in_sf(p['name'], sf_idx)
            if sf:
                p['position'] = sf['position']
                p['shirt']    = sf['shirt']
                if not p.get('flag') and sf['flag']:
                    p['flag']    = sf['flag']
                    p['country'] = sf['country']
                matched += 1
                changed += 1
            else:
                unmatched += 1

        status = f"✓ {matched}" + (f", {unmatched} sin match" if unmatched else "")
        print(status)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"✅ {league_key}_team_details.json guardado ({changed} jugadores)")

print("\n✅ Proceso completado.")
print("Reinicia el servidor (python app.py) y recarga http://localhost:8080")

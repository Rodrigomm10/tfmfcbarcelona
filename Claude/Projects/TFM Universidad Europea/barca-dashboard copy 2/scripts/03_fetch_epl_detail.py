"""
scripts/03_fetch_epl_detail.py
Cachea datos de la Premier League API (temporada 2025/26) para los 20 equipos.
Requiere internet. Ejecutar una vez: python scripts/03_fetch_epl_detail.py
"""
import urllib.request, json, os, time

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT     = os.path.join(BASE, "data", "processed")
SEASON  = 777   # 2025/26
COMP    = 1
API     = "https://footballapi.pulselive.com/football"

HEADERS = {
    "Origin":  "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def fetch_all_pages(url_base):
    items, page, num_pages = [], 0, 1
    while page < num_pages:
        data = fetch(f"{url_base}&page={page}&pageSize=100")
        items += data.get("content", [])
        num_pages = data.get("pageInfo", {}).get("numPages", 1)
        page += 1
    return items

print("Fetching EPL teams 2025/26...")
teams_raw = fetch(f"{API}/teams?comps={COMP}&compSeasons={SEASON}&pageSize=30")["content"]
teams = []
for t in teams_raw:
    ground = t.get("grounds", [{}])[0] if t.get("grounds") else {}
    teams.append({
        "id":       int(t["id"]),
        "name":     t["name"],
        "short":    t.get("shortName", t["name"]),
        "abbr":     t["club"]["abbr"],
        "stadium":  ground.get("name", ""),
        "city":     ground.get("city", ""),
        "capacity": int(ground.get("capacity", 0)) if ground.get("capacity") else 0,
    })
print(f"  {len(teams)} equipos")

KEY_STATS = [
    ("wins",                     "Victorias"),
    ("draws",                    "Empates"),
    ("losses",                   "Derrotas"),
    ("goals",                    "Goles marcados"),
    ("goals_conceded",           "Goles encajados"),
    ("clean_sheet",              "Porterías a cero"),
    ("total_scoring_att",        "Disparos totales"),
    ("ontarget_scoring_att",     "Disparos a puerta"),
    ("big_chance_created",       "Grandes ocasiones creadas"),
    ("big_chance_scored",        "Grandes ocasiones marcadas"),
    ("possession_percentage",    "Posesión (%)"),
    ("total_pass",               "Pases totales"),
    ("accurate_pass",            "Pases precisos"),
    ("total_tackle",             "Entradas totales"),
    ("won_tackle",               "Entradas ganadas"),
    ("aerial_won",               "Duelos aéreos ganados"),
    ("saves",                    "Paradas"),
    ("total_cross",              "Centros"),
    ("hit_woodwork",             "Golpes al poste"),
    ("total_yel_card",           "Tarjetas amarillas"),
]

all_data = {}

for team in teams:
    tid = team["id"]
    tname = team["name"]
    print(f"  Procesando {tname}...")

    # ── Plantilla ──
    try:
        squad_raw = fetch_all_pages(f"{API}/players?teams={tid}&compSeasons={SEASON}")
        squad = []
        for p in squad_raw:
            ct = p.get("currentTeam", {})
            if ct.get("id") != tid: continue  # excluir cedidos fuera
            info = p.get("info", {})
            name_d = p.get("name", {})
            squad.append({
                "id":       int(p.get("id", 0)),
                "playerId": int(p.get("playerId", 0)),
                "name":     name_d.get("display", ""),
                "shirt":    int(info.get("shirtNum", 0)) if info.get("shirtNum") else 0,
                "pos":      info.get("position", ""),
                "posInfo":  info.get("positionInfo", ""),
                "country":  p.get("nationalTeam", {}).get("country", ""),
                "flag":     p.get("nationalTeam", {}).get("isoCode", ""),
                "age":      p.get("age", ""),
            })
        squad.sort(key=lambda x: ("GDMF".index(x["pos"]) if x["pos"] in "GDMF" else 4, x["shirt"]))
    except Exception as e:
        print(f"    Squad error: {e}")
        squad = []

    # ── Estadísticas ──
    try:
        stats_raw = fetch(f"{API}/stats/team/{tid}?comps={COMP}&compSeasons={SEASON}&altIds=true")
        stats_map = {s["name"]: s["value"] for s in stats_raw.get("stats", [])}
        stats = []
        for key, label in KEY_STATS:
            val = stats_map.get(key)
            if val is not None:
                display = f"{val/len(teams_raw):.1f}" if "percentage" in key else str(int(val))
                if key == "possession_percentage" and val > 0:
                    display = f"{val/38:.1f}%" if val > 100 else f"{val:.1f}%"
                stats.append({"key": key, "label": label, "value": int(val) if val == int(val) else round(val, 1)})
    except Exception as e:
        print(f"    Stats error: {e}")
        stats = []

    # ── Partidos ──
    try:
        fixtures_raw = fetch(f"{API}/fixtures?teams={tid}&comps={COMP}&compSeasons={SEASON}&pageSize=50&sort=asc")
        matches = []
        for m in fixtures_raw.get("content", []):
            if m.get("status") != "C": continue  # solo jugados
            ts = m.get("teams", [])
            if len(ts) < 2: continue
            home_team = ts[0]["team"]["name"]
            away_team = ts[1]["team"]["name"]
            home_score = int(ts[0].get("score", 0) or 0)
            away_score = int(ts[1].get("score", 0) or 0)
            is_home = home_team == tname
            opp = away_team if is_home else home_team
            gf = home_score if is_home else away_score
            ga = away_score if is_home else home_score
            outcome = m.get("outcome", "")
            result = "W" if (is_home and outcome=="H") or (not is_home and outcome=="A") else \
                     "L" if (is_home and outcome=="A") or (not is_home and outcome=="H") else "D"
            kick_label = m.get("kickoff", {}).get("label", "")
            millis = m.get("kickoff", {}).get("millis", 0)
            matches.append({
                "id":       int(m.get("id", 0)),
                "gw":       int(m.get("gameweek", {}).get("gameweek", 0)),
                "date":     kick_label,
                "millis":   int(millis) if millis else 0,
                "home":     home_team,
                "away":     away_team,
                "homeScore":home_score,
                "awayScore":away_score,
                "isHome":   is_home,
                "opponent": opp,
                "gf":       gf,
                "ga":       ga,
                "result":   result,
            })
    except Exception as e:
        print(f"    Matches error: {e}")
        matches = []

    all_data[str(tid)] = {
        "team":    team,
        "squad":   squad,
        "stats":   stats,
        "matches": matches,
    }
    time.sleep(0.3)

# Guardar
out_path = os.path.join(OUT, "epl_teams_detail.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"season": "2025/26", "teams": all_data}, f, ensure_ascii=False)

total_players = sum(len(v["squad"]) for v in all_data.values())
total_matches = sum(len(v["matches"]) for v in all_data.values())
print(f"\n✅ epl_teams_detail.json guardado")
print(f"   Equipos: {len(all_data)} | Jugadores: {total_players} | Partidos: {total_matches}")

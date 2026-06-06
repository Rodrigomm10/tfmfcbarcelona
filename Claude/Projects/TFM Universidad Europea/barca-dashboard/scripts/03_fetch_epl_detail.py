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

# Etiquetas en español para las stats de la PL API
# Mapeamos las claves que devuelve la API con sus nombres oficiales
STAT_LABELS = {
    # Resultados
    "wins":                         "Victorias",
    "draws":                        "Empates",
    "losses":                       "Derrotas",
    # Ataque
    "goals":                        "Goles",
    "expected_goals":               "xG",
    "total_scoring_att":            "Intentos de gol totales",
    "ontarget_scoring_att":         "Disparos a puerta",
    "shot_off_target":              "Disparos fuera",
    "blocked_scoring_att":          "Disparos bloqueados",
    "att_ibox_goal":                "Goles dentro del área",
    "att_obox_goal":                "Goles fuera del área",
    "att_pen_goal":                 "Penaltis marcados",
    "att_pen_miss":                 "Penaltis fallados",
    "big_chance_created":           "Grandes ocasiones creadas",
    "big_chance_scored":            "Grandes ocasiones marcadas",
    "big_chance_missed":            "Grandes ocasiones falladas",
    "hit_woodwork":                 "Golpes al poste",
    "total_cross":                  "Centros intentados",
    "accurate_cross":               "Centros precisos",
    "att_hd_goal":                  "Goles de cabeza",
    "total_corners_intobox":        "Córneres al área",
    "corner_taken":                 "Córneres",
    "touches_in_opp_box":           "Toques en área rival",
    "total_freekick_goals":         "Goles de falta",
    # Posesión y pases
    "possession_percentage":        "Posesión (%)",
    "total_pass":                   "Pases totales",
    "accurate_pass":                "Pases precisos",
    "total_long_balls":             "Pases largos",
    "accurate_long_balls":          "Pases largos precisos",
    "total_through_ball":           "Pases en profundidad",
    "accurate_through_ball":        "Pases en profundidad precisos",
    # Defensa
    "goals_conceded":               "Goles encajados",
    "clean_sheet":                  "Porterías a cero",
    "saves":                        "Paradas",
    "total_tackle":                 "Entradas totales",
    "won_tackle":                   "Entradas ganadas",
    "interception":                 "Intercepciones",
    "total_clearance":              "Despejes",
    "blocked":                      "Bloqueos",
    "outfielder_block":             "Bloqueos de campo",
    "aerial_won":                   "Duelos aéreos ganados",
    "aerial_lost":                  "Duelos aéreos perdidos",
    "own_goals":                    "Goles en propia puerta",
    # Disciplina
    "total_yel_card":               "Tarjetas amarillas",
    "total_red_card":               "Tarjetas rojas",
    "foul_committed":               "Faltas cometidas",
    "total_offside":                "Fueras de juego",
    # Regate
    "dribble":                      "Regates intentados",
    "successful_dribble":           "Regates completados",
    "won_contest":                  "Duelos ganados",
    "total_contest":                "Duelos totales",
}

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
print(f"  {len(teams)} equipos encontrados")

all_data = {}

for team in teams:
    tid = team["id"]
    tname = team["name"]
    print(f"  Procesando {tname}...")

    # ── Plantilla ──
    # IMPORTANTE: no filtrar por currentTeam.id → incluye TODOS los jugadores
    # inscritos en la plantilla (incluyendo jóvenes con número alto como Saka, Saliba, etc.)
    try:
        squad_raw = fetch_all_pages(f"{API}/players?teams={tid}&compSeasons={SEASON}")
        squad = []
        for p in squad_raw:
            info    = p.get("info", {})
            name_d  = p.get("name", {})
            nat     = p.get("nationalTeam", {}) or {}
            squad.append({
                "id":       int(p.get("id", 0)),
                "playerId": int(p.get("playerId", 0)),
                "name":     name_d.get("display", ""),
                "shirt":    int(info.get("shirtNum", 0)) if info.get("shirtNum") else 0,
                "pos":      info.get("position", ""),
                "posInfo":  info.get("positionInfo", ""),
                "country":  nat.get("country", ""),
                "flag":     nat.get("isoCode", ""),
                "age":      p.get("age", ""),
            })
        # Ordenar por posición (G→D→M→F) y luego por dorsal
        pos_order = {"G": 0, "D": 1, "M": 2, "F": 3}
        squad.sort(key=lambda x: (pos_order.get(x["pos"], 4), x["shirt"] if x["shirt"] > 0 else 999))
        print(f"    Plantilla: {len(squad)} jugadores")
    except Exception as e:
        print(f"    Squad error: {e}")
        squad = []

    # ── Estadísticas — guardar TODAS las disponibles ──
    try:
        stats_raw = fetch(f"{API}/stats/team/{tid}?comps={COMP}&compSeasons={SEASON}&altIds=true")
        stats = []
        for s in stats_raw.get("stats", []):
            key = s["name"]
            val = s["value"]
            if val is None:
                continue
            # Convertir a número
            try:
                val_num = float(val)
            except (ValueError, TypeError):
                continue
            label = STAT_LABELS.get(key, key)  # si no tenemos label, usar el key
            stats.append({
                "key":   key,
                "label": label,
                "value": round(val_num, 2) if val_num != int(val_num) else int(val_num),
            })
        print(f"    Stats: {len(stats)} métricas")
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
            home_team  = ts[0]["team"]["name"]
            away_team  = ts[1]["team"]["name"]
            home_score = int(ts[0].get("score", 0) or 0)
            away_score = int(ts[1].get("score", 0) or 0)
            is_home    = home_team == tname
            opp        = away_team if is_home else home_team
            gf         = home_score if is_home else away_score
            ga         = away_score if is_home else home_score
            outcome    = m.get("outcome", "")
            result     = "W" if (is_home and outcome=="H") or (not is_home and outcome=="A") else \
                         "L" if (is_home and outcome=="A") or (not is_home and outcome=="H") else "D"
            kick_label = m.get("kickoff", {}).get("label", "")
            millis     = m.get("kickoff", {}).get("millis", 0)
            matches.append({
                "id":        int(m.get("id", 0)),
                "gw":        int(m.get("gameweek", {}).get("gameweek", 0)),
                "date":      kick_label,
                "millis":    int(millis) if millis else 0,
                "home":      home_team,
                "away":      away_team,
                "homeScore": home_score,
                "awayScore": away_score,
                "isHome":    is_home,
                "opponent":  opp,
                "gf":        gf,
                "ga":        ga,
                "result":    result,
            })
        print(f"    Partidos: {len(matches)}")
    except Exception as e:
        print(f"    Matches error: {e}")
        matches = []

    all_data[str(tid)] = {
        "team":    team,
        "squad":   squad,
        "stats":   stats,
        "matches": matches,
    }
    time.sleep(0.4)

# Guardar
out_path = os.path.join(OUT, "epl_teams_detail.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"season": "2025/26", "teams": all_data}, f, ensure_ascii=False)

total_players = sum(len(v["squad"]) for v in all_data.values())
total_matches = sum(len(v["matches"]) for v in all_data.values())
print(f"\n✅ epl_teams_detail.json guardado")
print(f"   Equipos:   {len(all_data)}")
print(f"   Jugadores: {total_players}")
print(f"   Partidos:  {total_matches}")
print(f"\nPasos siguientes:")
print(f"  1. Abre http://localhost:8080 y verifica la plantilla de Arsenal")
print(f"  2. Saka, Saliba y demás jugadores deberían aparecer ahora")

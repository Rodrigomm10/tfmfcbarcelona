"""
02_fetch_understat.py
Obtiene datos de Understat: xG, xGA, NPxG, xPTS por partido y liga.

Uso: python scripts/02_fetch_understat.py
"""

import json, re, os, time, urllib.request, urllib.error, html as html_module

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "data", "processed")
os.makedirs(OUT, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://understat.com/",
    "Upgrade-Insecure-Requests": "1",
}

LEAGUES = {
    "La_liga":    "es La Liga",
    "EPL":        "eng Premier League",
    "Bundesliga": "de Bundesliga",
    "Serie_A":    "it Serie A",
    "Ligue_1":    "fr Ligue 1",
}

# Understat: el año es el de INICIO de temporada.
# 2024 → temporada 2024/25 (última completa con 38 jornadas)
# 2025 → temporada 2025/26 (en curso o reciente)
SEASONS_TO_TRY = ["2025", "2024"]


def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        # Understat puede devolver gzip
        try:
            import gzip
            return gzip.decompress(raw).decode("utf-8")
        except Exception:
            return raw.decode("utf-8", errors="replace")


def extract_json_var(html_content, var_name):
    """Extrae variables JS embebidas. Soporta dos formatos de Understat."""
    # Formato 1: var teamsData = JSON.parse('...')
    p1 = rf"var\s+{var_name}\s*=\s*JSON\.parse\('(.+?)'\)"
    m = re.search(p1, html_content, re.DOTALL)
    if m:
        raw = m.group(1)
        # Understat usa \x escapes y HTML entities
        raw = raw.encode("utf-8").decode("unicode_escape")
        raw = html_module.unescape(raw)
        try:
            return json.loads(raw)
        except Exception:
            pass

    # Formato 2: var teamsData = JSON.parse(decodeURIComponent('...'))
    p2 = rf"var\s+{var_name}\s*=\s*JSON\.parse\(decodeURIComponent\('(.+?)'\)\)"
    m = re.search(p2, html_content, re.DOTALL)
    if m:
        from urllib.parse import unquote
        raw = unquote(m.group(1))
        try:
            return json.loads(raw)
        except Exception:
            pass

    return None


def fetch_league_data(league_key, season):
    url = f"https://understat.com/league/{league_key}/{season}"
    print(f"    GET {url}")
    html_content = fetch_url(url)
    teams_data = extract_json_var(html_content, "teamsData")
    dates_data = extract_json_var(html_content, "datesData")
    return teams_data, dates_data, html_content


def fetch_team_data(team_id, season):
    url = f"https://understat.com/team/{team_id}/{season}"
    print(f"    GET {url}")
    html_content = fetch_url(url)
    matches = extract_json_var(html_content, "datesData")
    players = extract_json_var(html_content, "playersData")
    stats   = extract_json_var(html_content, "statisticsData")
    return matches, players, stats


def get_barca_team_id(season):
    teams_data, _, _ = fetch_league_data("La_liga", season)
    if not teams_data:
        return None, None
    for team_id, tinfo in teams_data.items():
        title = tinfo.get("title", "")
        if "Barcelona" in title and "Espanyol" not in title:
            print(f"    → Barça: ID={team_id}, nombre={title}")
            return team_id, title
    return None, None


def build_table_entry(tdata, league_label):
    history = tdata.get("history", [])
    if not history:
        return None
    last = history[-1]
    return {
        "team":    tdata.get("title", ""),
        "team_id": None,
        "matches": int(last.get("matches", 0)),
        "wins":    int(last.get("wins", 0)),
        "draws":   int(last.get("draws", 0)),
        "loses":   int(last.get("loses", 0)),
        "scored":  int(last.get("scored", 0)),
        "missed":  int(last.get("missed", 0)),
        "pts":     int(last.get("pts", 0)),
        "gd":      int(last.get("scored", 0)) - int(last.get("missed", 0)),
        "xG":      round(sum(float(h.get("xG", 0)) for h in history), 2),
        "xGA":     round(sum(float(h.get("xGA", 0)) for h in history), 2),
        "npxG":    round(sum(float(h.get("npxG", 0)) for h in history), 2),
        "league":  league_label,
    }


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    all_league_tables = {}
    season_used = None

    print("\n1. Descargando tablas de ligas europeas (Understat)...")
    for season in SEASONS_TO_TRY:
        print(f"\n  Probando temporada {season} ({season}/{int(season)+1})...")
        season_success = 0
        temp_tables = {}

        for league_key, league_label in LEAGUES.items():
            try:
                teams_data, _, _ = fetch_league_data(league_key, season)
                if teams_data:
                    table = []
                    for tid, tdata in teams_data.items():
                        entry = build_table_entry(tdata, league_label)
                        if entry:
                            entry["team_id"] = tid
                            table.append(entry)
                    if table:
                        table.sort(key=lambda x: (-x["pts"], -x["gd"], -x["scored"]))
                        temp_tables[league_key] = table
                        season_success += 1
                        print(f"    ✓ {league_label}: {len(table)} equipos | Líder: {table[0]['team']} {table[0]['pts']}pts {table[0]['matches']}PJ | xG líder: {table[0]['xG']}")
                else:
                    print(f"    ✗ {league_label}: sin datos (teamsData vacío)")
                time.sleep(2)
            except Exception as e:
                print(f"    ✗ {league_label}: {e}")
                time.sleep(1)

        if season_success >= 3:
            all_league_tables = temp_tables
            season_used = season
            print(f"\n  → Usando temporada {season}: {season_success}/5 ligas descargadas")
            break
        else:
            print(f"  → Temporada {season} solo devolvió {season_success}/5 ligas, probando siguiente...")

    # Guardar si hay datos
    existing_path = os.path.join(OUT, "league_tables.json")
    if all_league_tables:
        try:
            with open(existing_path) as f:
                existing = json.load(f)
        except Exception:
            existing = {}
        existing.update(all_league_tables)
        with open(existing_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"\n✅ league_tables.json actualizado con {len(all_league_tables)} ligas (temporada {season_used})")
    else:
        print("\n⚠️  Understat no devolvió datos — league_tables.json sin cambios")
        print("   Posibles causas: bloqueo de IP, cambio en la web, o sin internet.")
        print("   Datos de Kaggle (sin xG) siguen activos.")

    # ─────────────────────────────────────────────
    print("\n2. Descargando datos detallados del FC Barcelona...")
    barca_season = season_used or SEASONS_TO_TRY[0]
    try:
        barca_id, barca_name = get_barca_team_id(barca_season)
        if barca_id:
            matches, players, stats = fetch_team_data(barca_id, barca_season)

            if matches:
                for m in matches:
                    try:
                        goals = m.get("goals", {})
                        if isinstance(goals, dict):
                            hg, ag = int(goals.get("h", 0)), int(goals.get("a", 0))
                        else:
                            hg, ag = 0, 0
                        is_home = m.get("side", "h") == "h"
                        gf = hg if is_home else ag
                        ga = ag if is_home else hg
                        m["gf"] = gf
                        m["ga"] = ga
                        m["result"] = "W" if gf > ga else ("D" if gf == ga else "L")
                    except Exception:
                        pass
                with open(os.path.join(OUT, "barca_matches_understat.json"), "w", encoding="utf-8") as f:
                    json.dump(matches, f, ensure_ascii=False, indent=2)
                print(f"    ✓ {len(matches)} partidos del Barça (Understat, temporada {barca_season})")

            if players:
                with open(os.path.join(OUT, "barca_players_understat.json"), "w", encoding="utf-8") as f:
                    json.dump(players, f, ensure_ascii=False, indent=2)
                print(f"    ✓ {len(players)} jugadores del Barça (Understat)")

            if stats:
                with open(os.path.join(OUT, "barca_stats_understat.json"), "w", encoding="utf-8") as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                print("    ✓ Estadísticas del Barça guardadas (Understat)")
        else:
            print(f"    ✗ Barça no encontrado en La Liga temporada {barca_season}")
            print("      Equipos encontrados en Understat (para debug):")
            try:
                teams_data, _, _ = fetch_league_data("La_liga", barca_season)
                if teams_data:
                    for tid, t in list(teams_data.items())[:6]:
                        print(f"        - {t.get('title','?')} (id:{tid})")
            except Exception:
                pass
    except Exception as e:
        print(f"    ✗ Error datos Barça: {e}")

    print("\n✅ Script completado.")
    print(f"   Archivos en: {OUT}")

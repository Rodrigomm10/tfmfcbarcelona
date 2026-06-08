"""
01_process_data.py
Limpia y filtra los CSV de Kaggle para el dashboard del FC Barcelona.
Salida: archivos JSON en data/processed/
"""

import pandas as pd
import json
import os

import polars as pl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(BASE, "data", "processed")
os.makedirs(OUT, exist_ok=True)

BARCA_NAMES = {"FC Barcelona", "Barcelona", "Fútbol Club Barcelona"}
BARCA_ID = 131  # Transfermarkt club_id del Barça


# ─────────────────────────────────────────────
# 1. PARTIDOS (games.csv)
# ─────────────────────────────────────────────

### Arreglando esta miesh 



print("Procesando games.csv...")
games = pd.read_csv(os.path.join(RAW, "games.csv"), low_memory=False)


hg = pl.col("home_club_goals").cast(pl.Int32, strict = False)
ag = pl.col("away_club_goals").cast(pl.Int32, strict = False) # Make sure the goals are right data type

is_home = (
        (pl.col('home_club_id').cast(pl.String) == str(BARCA_ID)) | 
        (pl.col('home_club_name').cast(pl.String) == str(BARCA_NAMES)))

is_away = (
        (pl.col('away_club_id').cast(pl.String) == str(BARCA_ID)) | 
        (pl.col('away_club_name').cast(pl.String) == str(BARCA_NAMES))
        )

gf = pl.when(is_home).then(hg).when(is_away).then(ag).otherwise(None) #asegurarnos los goles a favor y encontra
ga = pl.when(is_home).then(ag).when(is_away).then(hg).otherwise(None)

barca_result_expr = (
        pl.when(gf.is_null() | ga.is_null()).then(None)
        .when(gf > ga).then(pl.lit("W"))
        .when(gf == ga).then(pl.lit("D"))
        .otherwise(pl.lit('L'))
        )

# Aplicamos las expresiones
games_andres = (
        pl.scan_csv('data\\raw\\games.csv', try_parse_dates = True)
        .filter(( pl.col('season').is_in([2025]) ) & ((pl.col('home_club_id') == BARCA_ID)|(pl.col('away_club_id') == BARCA_ID)))
        .with_columns(
            barca_result = barca_result_expr
            )
        .select(cols_games)
        )

games_andres = games_andres.collect() # colectar con polars

games_andres = games_andres.to_pandas()
games_andres.to_json("data\\processed\\barca_games_2.json", orient="records", force_ascii=False)

### Escribir el JSON

games_andres.write_ndjson('data\\processed\\barca_games_2.json')

# Filtrar temporada 2024/2025 y 2025/2026
games = games[games["season"].isin([2024, 2025])]

# Mantener columnas útiles
cols_games = [
    "game_id", "competition_id", "season", "round", "date",
    "home_club_id", "away_club_id", "home_club_goals", "away_club_goals",
    "home_club_name", "away_club_name", "home_club_formation", "away_club_formation",
    "stadium", "attendance", "referee"
]
cols_games = [c for c in cols_games if c in games.columns]
games = games[cols_games].copy()

# Añadir columna resultado relativo al Barça
def barca_result(row):
    is_home = str(row.get("home_club_id", "")) == str(BARCA_ID) or \
              row.get("home_club_name", "") in BARCA_NAMES
    is_away = str(row.get("away_club_id", "")) == str(BARCA_ID) or \
              row.get("away_club_name", "") in BARCA_NAMES
    try:
        hg, ag = int(row["home_club_goals"]), int(row["away_club_goals"])
    except (ValueError, TypeError):
        return None
    if is_home:
        gf, ga = hg, ag
    elif is_away:
        gf, ga = ag, hg
    else:
        return None
    return "W" if gf > ga else ("D" if gf == ga else "L")

games["barca_result"] = games.apply(barca_result, axis=1)

# Guardar todos los partidos y solo los del Barça
games.to_json(os.path.join(OUT, "games_all.json"), orient="records", force_ascii=False)
barca_games = games[
    (games["home_club_id"].astype(str) == str(BARCA_ID)) |
    (games["away_club_id"].astype(str) == str(BARCA_ID)) |
    (games["home_club_name"].isin(BARCA_NAMES)) |
    (games["away_club_name"].isin(BARCA_NAMES))
]
barca_games.to_json(os.path.join(OUT, "barca_games.json"), orient="records", force_ascii=False)
print(f"  → {len(barca_games)} partidos del Barça guardados")

# Partidos por competición
COMP_MAP = {
    "ES1":  "La Liga",
    "CL":   "Champions League",
    "CDR":  "Copa del Rey",
    "SUC":  "Supercopa",
    "EL":   "Europa League",
    "ECLQ": "Conference League",
}
for comp_id, comp_name in COMP_MAP.items():
    comp_games = barca_games[barca_games["competition_id"] == comp_id].copy()
    if not comp_games.empty:
        fname = f"barca_{comp_id.lower()}_games.json"
        comp_games.to_json(os.path.join(OUT, fname), orient="records", force_ascii=False)
        print(f"  → {len(comp_games)} partidos de {comp_name} guardados ({fname})")


# ─────────────────────────────────────────────
# 2. JUGADORES – STATS 2025/26 (players_data-2025_2026.csv)
# ─────────────────────────────────────────────
print("Procesando players_data-2025_2026.csv...")
players = pd.read_csv(os.path.join(RAW, "players_data-2025_2026.csv"), low_memory=False)

# Jugadores del Barça
barca_players = players[players["Squad"].str.contains("Barcelona", na=False)].copy()

# Columnas base relevantes
base_cols = [
    "Player", "Nation", "Pos", "Squad", "Comp", "Age", "Born",
    "MP", "Starts", "Min", "90s", "Gls", "Ast", "G+A", "G-PK",
    "CrdY", "CrdR",
    # Porteros
    "GA", "GA90", "SoTA", "Saves", "Save%", "CS", "CS%",
    # Disparo
    "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh",
    # Tiempo de juego
    "Mn/MP", "Min%", "Starts_stats_playing_time", "Subs", "PPM",
    # Misc
    "Fls", "Fld", "Int", "TklW", "Off",
]
base_cols = [c for c in base_cols if c in players.columns]

# Columnas de estadísticas avanzadas
adv_cols = [
    "Player", "Pos", "Squad", "Comp", "Age", "90s",
    # Disparo avanzado
    "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT",
    # Tiempo de juego
    "MP", "Starts", "Min", "Mn/MP", "Min%", "Subs", "PPM",
    "onG", "onGA", "+/-", "+/-90",
    # Disciplina / duelos
    "Fls", "Fld", "Int", "TklW", "Off", "CrdY", "CrdR",
    # Porteros
    "GA", "GA90", "SoTA", "Saves", "Save%", "CS", "CS%",
]
adv_cols = [c for c in adv_cols if c in players.columns]

# Guardar todos (para comparativa de ligas) y solo Barça
players[base_cols].to_json(os.path.join(OUT, "players_all.json"), orient="records", force_ascii=False)
barca_players[base_cols].to_json(os.path.join(OUT, "barca_players.json"), orient="records", force_ascii=False)
barca_players[adv_cols].to_json(os.path.join(OUT, "barca_players_advanced.json"), orient="records", force_ascii=False)
print(f"  → {len(barca_players)} jugadores del Barça guardados (base + avanzado)")

# Top jugadores por liga (para comparativa)
top_by_league = players[base_cols].copy()
top_by_league.to_json(os.path.join(OUT, "players_by_league.json"), orient="records", force_ascii=False)


# ─────────────────────────────────────────────
# 3. TRANSFERENCIAS (transfers.csv)
# ─────────────────────────────────────────────
print("Procesando transfers.csv...")
transfers = pd.read_csv(os.path.join(RAW, "transfers.csv"), low_memory=False)

# Barça como origen o destino
barca_transfers = transfers[
    (transfers["from_club_name"].str.contains("Barcelona", na=False)) |
    (transfers["to_club_name"].str.contains("Barcelona", na=False))
].copy()

# Convertir fee a numérico
barca_transfers["transfer_fee"] = pd.to_numeric(barca_transfers["transfer_fee"], errors="coerce")
barca_transfers["market_value_in_eur"] = pd.to_numeric(barca_transfers["market_value_in_eur"], errors="coerce")

# Clasificar: entrada o salida
barca_transfers["direction"] = barca_transfers.apply(
    lambda r: "IN" if "Barcelona" in str(r.get("to_club_name", "")) else "OUT", axis=1
)

barca_transfers.to_json(os.path.join(OUT, "barca_transfers.json"), orient="records", force_ascii=False)
print(f"  → {len(barca_transfers)} transferencias del Barça guardadas")


# ─────────────────────────────────────────────
# 4. VALORACIONES DE MERCADO (player_valuations.csv)
# ─────────────────────────────────────────────
print("Procesando player_valuations.csv...")
valuations = pd.read_csv(os.path.join(RAW, "player_valuations.csv"), low_memory=False)

# Solo las más recientes (último registro por jugador del Barça)
barca_val = valuations[valuations["current_club_name"].str.contains("Barcelona", na=False)].copy()
barca_val["date"] = pd.to_datetime(barca_val["date"], errors="coerce")
barca_val_latest = barca_val.sort_values("date").groupby("player_id").last().reset_index()

barca_val_latest.to_json(os.path.join(OUT, "barca_valuations.json"), orient="records", force_ascii=False)

# Para el gráfico de evolución del valor total de plantilla
plantilla_value = (
    barca_val.groupby("date")["market_value_in_eur"]
    .sum()
    .reset_index()
    .sort_values("date")
)
plantilla_value["date"] = plantilla_value["date"].astype(str)
plantilla_value.to_json(os.path.join(OUT, "barca_squad_value_history.json"), orient="records", force_ascii=False)
print(f"  → {len(barca_val_latest)} valoraciones del Barça guardadas")


# ─────────────────────────────────────────────
# 5. RESUMEN DE COMPETICIONES DISPONIBLES
# ─────────────────────────────────────────────
if "competition_id" in games.columns:
    competitions = games["competition_id"].unique().tolist()
    with open(os.path.join(OUT, "competitions.json"), "w") as f:
        json.dump(competitions, f)


# ─────────────────────────────────────────────
# 6. PREMIER LEAGUE — Understat CSVs
# ─────────────────────────────────────────────
import csv as csvlib

EPL_NAMES = {
    'Arsenal':'Arsenal','Manchester City':'Manchester City',
    'Manchester United':'Manchester United','Aston Villa':'Aston Villa',
    'Liverpool':'Liverpool','Bournemouth':'Bournemouth','Sunderland':'Sunderland',
    'Brighton':'Brighton & Hove Albion','Brentford':'Brentford','Chelsea':'Chelsea',
    'Fulham':'Fulham','Newcastle United':'Newcastle United','Everton':'Everton',
    'Leeds':'Leeds United','Crystal Palace':'Crystal Palace',
    'Nottingham Forest':'Nottingham Forest','Tottenham':'Tottenham Hotspur',
    'West Ham':'West Ham United','Burnley':'Burnley',
    'Wolverhampton Wanderers':'Wolverhampton Wanderers',
}
KAGGLE_TO_EPL = {
    'Arsenal Football Club':'Arsenal',
    'Association Football Club Bournemouth':'Bournemouth',
    'Aston Villa Football Club':'Aston Villa',
    'Brentford Football Club':'Brentford',
    'Brighton and Hove Albion Football Club':'Brighton',
    'Burnley Football Club':'Burnley',
    'Chelsea Football Club':'Chelsea',
    'Crystal Palace Football Club':'Crystal Palace',
    'Everton Football Club':'Everton',
    'Fulham Football Club':'Fulham',
    'Leeds United Association Football Club':'Leeds',
    'Liverpool Football Club':'Liverpool',
    'Manchester City Football Club':'Manchester City',
    'Manchester United Football Club':'Manchester United',
    'Newcastle United Football Club':'Newcastle United',
    'Nottingham Forest Football Club':'Nottingham Forest',
    'Sunderland Association Football Club':'Sunderland',
    'Tottenham Hotspur Football Club':'Tottenham',
    'West Ham United Football Club':'West Ham',
    'Wolverhampton Wanderers Football Club':'Wolverhampton Wanderers',
}

epl_table_path   = os.path.join(RAW, "epl_understat_table.csv")
epl_home_path    = os.path.join(RAW, "epl_understat_home.csv")
epl_away_path    = os.path.join(RAW, "epl_understat_away.csv")
epl_players_path = os.path.join(RAW, "epl_understat_players.csv")

if os.path.exists(epl_table_path) and os.path.exists(epl_players_path):
    print("Procesando Premier League Understat CSVs...")

    def parse_epl_table_csv(path):
        rows = []
        with open(path, encoding='utf-8-sig') as f:
            for row in csvlib.DictReader(f, delimiter=';'):
                name = EPL_NAMES.get(row['team'], row['team'])
                rows.append({
                    'team':    name,
                    'matches': int(row['matches']),
                    'wins':    int(row['wins']),
                    'draws':   int(row['draws']),
                    'loses':   int(row['loses']),
                    'scored':  int(row['goals']),
                    'missed':  int(row['ga']),
                    'gd':      int(row['goals']) - int(row['ga']),
                    'pts':     int(row['points']),
                    'xG':      round(float(row['xG']),   2),
                    'xGA':     round(float(row['xGA']),  2),
                    'xPTS':    round(float(row['xPTS']), 2),
                })
        rows.sort(key=lambda x: (-x['pts'], -x['gd'], -x['scored']))
        return rows

    epl_total = parse_epl_table_csv(epl_table_path)

    # epl_table.json (con position explícita, para KPIs)
    epl_table_out = [dict(r, position=i+1) for i, r in enumerate(epl_total)]
    with open(os.path.join(OUT, "epl_table.json"), 'w') as f:
        json.dump(epl_table_out, f, ensure_ascii=False)
    print(f"  → epl_table.json: {len(epl_table_out)} equipos")

    # epl_splits.json — total + home + away con xG/xGA/xPTS
    epl_home = parse_epl_table_csv(epl_home_path) if os.path.exists(epl_home_path) else []
    epl_away = parse_epl_table_csv(epl_away_path) if os.path.exists(epl_away_path) else []
    with open(os.path.join(OUT, "epl_splits.json"), 'w') as f:
        json.dump({'total': epl_total, 'home': epl_home, 'away': epl_away}, f, ensure_ascii=False)
    print(f"  → epl_splits.json: total={len(epl_total)}, home={len(epl_home)}, away={len(epl_away)}")

    # Jugadores
    epl_players = []
    with open(epl_players_path, encoding='utf-8-sig') as f:
        for row in csvlib.DictReader(f, delimiter=';'):
            team = EPL_NAMES.get(row['team'], row['team'])
            epl_players.append({
                'player': row['player'], 'team': team,
                'apps': int(row['apps']), 'min': int(row['min']),
                'goals': int(row['goals']), 'assists': int(row['a']),
                'xG': round(float(row['xG']), 2),
                'xA': round(float(row['xA']), 2),
            })
    with open(os.path.join(OUT, "epl_players.json"), 'w') as f:
        json.dump(epl_players, f, ensure_ascii=False)
    print(f"  → epl_players.json: {len(epl_players)} jugadores")

    # Progresión desde Kaggle games.csv + extensión a JJ38 con pts finales
    final_pts = {r['team']: r['pts'] for r in epl_total}
    epl_games = [
        r for r in games.to_dict('records')
        if r.get('competition_id') == 'GB1' and str(r.get('season', '')) == '2025'
    ]
    def rnd_num(r):
        try: return int(str(r.get('round', '')).split('.')[0])
        except: return 99
    parsed = []
    for g in epl_games:
        h = KAGGLE_TO_EPL.get(str(g.get('home_club_name', '')))
        a = KAGGLE_TO_EPL.get(str(g.get('away_club_name', '')))
        try: hg, ag = int(g['home_club_goals']), int(g['away_club_goals'])
        except: continue
        rnd = rnd_num(g)
        if h and a and rnd < 90:
            parsed.append({'round': rnd, 'home': EPL_NAMES.get(h, h), 'away': EPL_NAMES.get(a, a), 'hg': hg, 'ag': ag})

    max_rnd = max((g['round'] for g in parsed), default=0)
    all_teams = list(final_pts.keys())
    cum = {t: 0 for t in all_teams}
    jornadas, tdata = [], {t: [] for t in all_teams}
    for rnd in range(1, max_rnd + 1):
        for g in (g for g in parsed if g['round'] == rnd):
            if g['hg'] > g['ag']:    cum[g['home']] += 3
            elif g['hg'] == g['ag']: cum[g['home']] += 1; cum[g['away']] += 1
            else:                    cum[g['away']] += 3
        if any(g['round'] == rnd for g in parsed):
            jornadas.append(rnd)
            for t in all_teams: tdata[t].append(cum[t])

    last = max(jornadas, default=0)
    for rnd in range(last + 1, 39):
        jornadas.append(rnd)
        for t in all_teams:
            pts_last = tdata[t][-1] if tdata[t] else 0
            remaining = 38 - (rnd - 1)
            diff = final_pts.get(t, pts_last) - pts_last
            inc = round(diff / remaining) if remaining > 0 else 0
            tdata[t].append(min(pts_last + inc, final_pts.get(t, pts_last)))
    for t in all_teams:
        if tdata[t]: tdata[t][-1] = final_pts.get(t, tdata[t][-1])

    with open(os.path.join(OUT, "epl_progression.json"), 'w') as f:
        json.dump({'matchdays': jornadas, 'teams': tdata}, f, ensure_ascii=False)
    print(f"  → epl_progression.json: {len(jornadas)} jornadas")
else:
    print("  ⚠️  CSVs de Premier League no encontrados en data/raw/")

print("\n✅ Procesamiento completado. Archivos en data/processed/")

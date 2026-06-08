"""
app.py – Servidor Flask del dashboard FC Barcelona
Ejecutar: python app.py
Acceder:  http://localhost:5000
"""

import os
import json
from flask import Flask, jsonify, render_template, abort

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(BASE, "data", "processed")


def load_json(filename):
    path = os.path.join(PROCESSED, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─── FRONTEND ────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─── API: PARTIDOS ────────────────────────────
@app.route("/api/barca/games")
def barca_games():
    data = load_json("barca_games_2.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/matches/understat")
def barca_matches_understat():
    data = load_json("barca_matches_understat.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/02_fetch_understat.py para obtener estos datos"}), 404
    return jsonify(data)


# ─── API: JUGADORES ──────────────────────────
@app.route("/api/barca/players")
def barca_players():
    data = load_json("barca_players.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/players/understat")
def barca_players_understat():
    data = load_json("barca_players_understat.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/02_fetch_understat.py"}), 404
    return jsonify(data)


# ─── API: PLANTILLA / MERCADO ────────────────
@app.route("/api/barca/transfers")
def barca_transfers():
    data = load_json("barca_transfers.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/valuations")
def barca_valuations():
    data = load_json("barca_valuations.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/squad-value-history")
def squad_value_history():
    data = load_json("barca_squad_value_history.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── API: COMPETICIONES ──────────────────────
@app.route("/api/barca/champions")
def barca_champions():
    data = load_json("barca_cl_games.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/copadelrey")
def barca_copa():
    data = load_json("barca_cdr_games.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/barca/supercopa")
def barca_supercopa():
    data = load_json("barca_suc_games.json")
    if data is None:
        return jsonify([]), 200
    return jsonify(data)


# ─── API: STATS AVANZADAS ────────────────────
@app.route("/api/barca/players/advanced")
def barca_players_advanced():
    data = load_json("barca_players_advanced.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── API: LA LIGA PROGRESSION ────────────────
@app.route("/api/laliga/progression")
def laliga_progression():
    data = load_json("laliga_progression.json")
    if data is None:
        return jsonify({"error": "Sin datos"}), 404
    return jsonify(data)


# ─── API: LA LIGA UNDERSTAT PLAYERS ──────────
@app.route("/api/laliga/players")
def laliga_players():
    data = load_json("laliga_players_understat.json")
    if data is None:
        return jsonify([]), 200
    return jsonify(data)


# ─── API: LA LIGA SPLITS ─────────────────────
@app.route("/api/laliga/splits")
def laliga_splits():
    data = load_json("laliga_splits.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── API: PREMIER LEAGUE ─────────────────────
@app.route("/api/epl/table")
def epl_table():
    data = load_json("epl_table.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/process_epl.py"}), 404
    return jsonify(data)


@app.route("/api/epl/players")
def epl_players():
    data = load_json("epl_players.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/process_epl.py"}), 404
    return jsonify(data)


@app.route("/api/epl/progression")
def epl_progression():
    data = load_json("epl_progression.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/process_epl.py"}), 404
    return jsonify(data)


@app.route("/api/epl/splits")
def epl_splits():
    data = load_json("epl_splits.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── API: EPL TEAM DETAIL ────────────────────
@app.route("/api/epl/teams/detail")
def epl_teams_detail():
    data = load_json("epl_teams_detail.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/03_fetch_epl_detail.py"}), 404
    return jsonify(data)

@app.route("/api/epl/understat-squads")
def epl_understat_squads():
    data = load_json("epl_understat_squads.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/04_fetch_epl_understat_squads.py"}), 404
    return jsonify(data)

@app.route("/api/laliga/teams/detail")
def laliga_teams_detail():
    data = load_json("laliga_team_details.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/05_generate_league_team_details.py"}), 404
    return jsonify(data)

@app.route("/api/bundesliga/teams/detail")
def bundesliga_teams_detail():
    data = load_json("bundesliga_team_details.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/05_generate_league_team_details.py"}), 404
    return jsonify(data)

@app.route("/api/seriea/teams/detail")
def seriea_teams_detail():
    data = load_json("seriea_team_details.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/05_generate_league_team_details.py"}), 404
    return jsonify(data)

@app.route("/api/ligue1/teams/detail")
def ligue1_teams_detail():
    data = load_json("ligue1_team_details.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/05_generate_league_team_details.py"}), 404
    return jsonify(data)

# ─── API: LIGUE 1 ────────────────────────────
@app.route("/api/ligue1/splits")
def ligue1_splits():
    data = load_json("ligue1_splits.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/ligue1/players")
def ligue1_players():
    data = load_json("ligue1_players.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/ligue1/progression")
def ligue1_progression():
    data = load_json("ligue1_progression.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

# ─── API: SERIE A ────────────────────────────
@app.route("/api/seriea/splits")
def seriea_splits():
    data = load_json("seriea_splits.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/seriea/players")
def seriea_players():
    data = load_json("seriea_players.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/seriea/progression")
def seriea_progression():
    data = load_json("seriea_progression.json")
    if data is None: return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

# ─── API: BUNDESLIGA ─────────────────────────
@app.route("/api/bundesliga/splits")
def bundesliga_splits():
    data = load_json("bundesliga_splits.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/bundesliga/players")
def bundesliga_players():
    data = load_json("bundesliga_players.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

@app.route("/api/bundesliga/progression")
def bundesliga_progression():
    data = load_json("bundesliga_progression.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)

# ─── API: TABLAS UCL / UEL ───────────────────
@app.route("/api/ucl/table")
def ucl_table():
    data = load_json("ucl_table.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


@app.route("/api/uel/table")
def uel_table():
    data = load_json("uel_table.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── API: COMPARATIVA EUROPA ─────────────────
@app.route("/api/leagues/tables")
def league_tables():
    data = load_json("league_tables.json")
    if data is None:
        return jsonify({"error": "Ejecuta scripts/02_fetch_understat.py"}), 404
    return jsonify(data)


@app.route("/api/leagues/players")
def all_players():
    data = load_json("players_all.json")
    if data is None:
        return jsonify({"error": "Datos no encontrados. Ejecuta scripts/01_process_data.py"}), 404
    return jsonify(data)


# ─── ESTADO DEL SISTEMA ──────────────────────
@app.route("/api/status")
def status():
    files = [
        "barca_games.json",
        "barca_cl_games.json",
        "barca_cdr_games.json",
        "barca_players.json",
        "barca_players_advanced.json",
        "barca_transfers.json",
        "barca_valuations.json",
        "barca_matches_understat.json",
        "barca_players_understat.json",
        "league_tables.json",
        "players_all.json",
    ]
    result = {}
    for f in files:
        path = os.path.join(PROCESSED, f)
        result[f] = os.path.exists(path)
    return jsonify(result)



#### Prueba de como funciona esta miesh

@app.route("/api/barca/lesiones")
def barca_lesiones():
    data = load_json("barca_lesiones.json")
    if data is None:
        return jsonify({"Error": "No se encontro el archivo"}), 404
    return jsonify(data)


if __name__ == "__main__":
    print("\n🔵 FC Barcelona Dashboard")
    print("   Abre tu navegador en: http://localhost:8080\n")
    app.run(debug=True, port=8080)

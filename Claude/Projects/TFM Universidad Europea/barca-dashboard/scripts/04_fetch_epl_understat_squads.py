"""
scripts/04_fetch_epl_understat_squads.py
Genera epl_understat_squads.json a partir de los datos Understat ya disponibles
en data/raw/epl_understat_players.csv, enriquecidos con la info de la PL API
(fotos, dorsal, bandera, posición) de epl_teams_detail.json.

NO requiere internet. Ejecutar: python scripts/04_fetch_epl_understat_squads.py
"""
import csv, json, os, unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "data", "raw")
OUT  = os.path.join(BASE, "data", "processed")

# ── Normalización de nombres ───────────────────────────────────────────────────
# Tabla de caracteres que NFD NO descompone (no son base + combining mark)
_SPECIAL = str.maketrans({
    'ø': 'o', 'Ø': 'o',
    'ð': 'd', 'Ð': 'd',
    'þ': 'th','Þ': 'th',
    'ß': 'ss',
    'æ': 'ae','Æ': 'ae',
    'ł': 'l', 'Ł': 'l',
    'đ': 'd', 'Đ': 'd',
    'ŋ': 'n', 'Ŋ': 'n',
    'œ': 'oe','Œ': 'oe',
    'ø': 'o',  # ø (redundante pero explícito)
})

def normalize(s):
    """Quita tildes y caracteres especiales; pasa a minúsculas."""
    s = (s or '').translate(_SPECIAL)
    nfkd = unicodedata.normalize('NFD', s)
    base = ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')
    return base.lower().strip()

# ── Mapa CSV Understat → nombre oficial PL API ────────────────────────────────
CSV_TO_PL = {
    'Arsenal':                 'Arsenal',
    'Aston Villa':             'Aston Villa',
    'Bournemouth':             'Bournemouth',
    'Brentford':               'Brentford',
    'Brighton':                'Brighton & Hove Albion',
    'Burnley':                 'Burnley',
    'Chelsea':                 'Chelsea',
    'Crystal Palace':          'Crystal Palace',
    'Everton':                 'Everton',
    'Fulham':                  'Fulham',
    'Leeds':                   'Leeds United',
    'Liverpool':               'Liverpool',
    'Manchester City':         'Manchester City',
    'Manchester United':       'Manchester United',
    'Newcastle United':        'Newcastle United',
    'Nottingham Forest':       'Nottingham Forest',
    'Sunderland':              'Sunderland',
    'Tottenham':               'Tottenham Hotspur',
    'West Ham':                'West Ham United',
    'Wolverhampton Wanderers': 'Wolverhampton Wanderers',
}

# ── Posición PL API → código estándar ────────────────────────────────────────
def map_pos(pos_str):
    p = (pos_str or '').strip().upper()
    if p == 'G':  return 'G'
    if p == 'D':  return 'D'
    if p == 'M':  return 'M'
    if p == 'F':  return 'F'
    return 'M'

# ── Leer CSV Understat ────────────────────────────────────────────────────────
csv_path = os.path.join(RAW, 'epl_understat_players.csv')
print(f'Leyendo {csv_path}…')
raw_players = []
with open(csv_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        mins = int(row.get('min', 0) or 0)
        apps = int(row.get('apps', 0) or 0)
        if mins == 0 and apps == 0:
            continue
        raw_players.append({
            'name':    row['player'].strip(),
            'team':    row['team'].strip(),
            'apps':    apps,
            'min':     mins,
            'goals':   int(float(row.get('goals', 0) or 0)),
            'assists': int(float(row.get('a',     0) or 0)),
        })
print(f'  {len(raw_players)} jugadores con minutos > 0')

# ── Leer datos PL API ─────────────────────────────────────────────────────────
detail_path = os.path.join(OUT, 'epl_teams_detail.json')
pl_squad_by_pl_name = {}
if os.path.exists(detail_path):
    with open(detail_path, encoding='utf-8') as f:
        pl_detail = json.load(f)
    for tid, tdata in pl_detail.get('teams', {}).items():
        pl_squad_by_pl_name[tdata['team']['name']] = tdata.get('squad', [])
    print(f'  {len(pl_squad_by_pl_name)} equipos cargados de epl_teams_detail.json')
else:
    print('  ⚠️  epl_teams_detail.json no encontrado — sin fotos ni dorsales')

# ── Índice y búsqueda ─────────────────────────────────────────────────────────
def make_pl_index(pl_squad):
    """Construye índice normalizado → jugador PL API."""
    idx = {}
    for p in pl_squad:
        key = normalize(p['name'])
        # Guardar solo el primero con ese nombre normalizado (evita duplicados)
        if key not in idx:
            idx[key] = p
    return idx

def find_pl(name, pl_idx):
    """
    Busca un jugador PL API por nombre Understat.
    Estrategia: exacto → apellido → primer nombre (único o menor dorsal).
    """
    n = normalize(name)
    tokens = n.split()

    # 1. Coincidencia exacta
    if n in pl_idx:
        return pl_idx[n]

    # 2. Coincidencia por apellido (última palabra)
    if len(tokens) > 1:
        last = tokens[-1]
        # Solo si el apellido tiene 4+ letras (evita falsos positivos con "da", "de", etc.)
        if len(last) >= 4:
            matches = [v for k, v in pl_idx.items() if k.endswith(' ' + last)]
            if len(matches) == 1:
                return matches[0]

    # 3. Coincidencia por primer nombre (útil para jugadores de un solo nombre)
    first = tokens[0] if tokens else ''
    if len(first) >= 4:
        matches = [v for k, v in pl_idx.items() if k.startswith(first + ' ') or k == first]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            # Desambiguar: tomar el jugador con menor dorsal (suele ser el titular)
            valid = [m for m in matches if m.get('shirt', 0) > 0]
            if valid:
                return min(valid, key=lambda x: x['shirt'])

    return None

# ── Agrupar jugadores por equipo ──────────────────────────────────────────────
by_pl_team = {pl: [] for pl in CSV_TO_PL.values()}

for p in raw_players:
    primary_csv_team = p['team'].split(',')[0].strip()
    pl_name = CSV_TO_PL.get(primary_csv_team)
    if pl_name is None:
        # Búsqueda flexible
        pl_name = next((v for k, v in CSV_TO_PL.items()
                        if normalize(k) == normalize(primary_csv_team)), None)
    if pl_name is None:
        continue
    by_pl_team[pl_name].append(p)

# ── Enriquecer con datos PL API y ordenar ─────────────────────────────────────
POS_ORDER = {'G': 0, 'D': 1, 'M': 2, 'F': 3}
all_squads = {}
total = 0
unmatched_total = 0

for pl_name, players in by_pl_team.items():
    pl_squad = pl_squad_by_pl_name.get(pl_name, [])
    pl_idx   = make_pl_index(pl_squad)
    enriched = []
    unmatched = []

    for p in players:
        pl = find_pl(p['name'], pl_idx)
        if pl is None:
            unmatched.append(p['name'])
        enriched.append({
            'name':     p['name'],
            'position': map_pos(pl['pos']) if pl else 'M',
            'games':    p['apps'],
            'goals':    p['goals'],
            'assists':  p['assists'],
            'minutes':  p['min'],
            'playerId': pl['playerId'] if pl else 0,
            'shirt':    pl['shirt']    if pl else 0,
            'country':  pl['country']  if pl else '',
            'flag':     pl['flag']     if pl else '',
        })

    enriched.sort(key=lambda x: (POS_ORDER.get(x['position'], 4), -x['minutes']))
    all_squads[pl_name] = enriched
    total += len(enriched)
    unmatched_total += len(unmatched)

    status = f'({len(unmatched)} sin foto: {", ".join(unmatched)})' if unmatched else '✓ todos emparejados'
    print(f'  {pl_name}: {len(enriched)} jugadores — {status}')

# ── Guardar ───────────────────────────────────────────────────────────────────
out_path = os.path.join(OUT, 'epl_understat_squads.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump({'season': '2025/26', 'teams': all_squads}, f,
              ensure_ascii=False, indent=2)

matched_pct = 100 * (total - unmatched_total) // total if total else 0
print(f'\n✅ epl_understat_squads.json guardado')
print(f'   Equipos: {len(all_squads)} | Jugadores: {total} | Con foto: {matched_pct}%')
print('\nReinicia el servidor (python app.py) y recarga http://localhost:8080')

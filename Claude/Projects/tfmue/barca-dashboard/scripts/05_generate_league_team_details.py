"""
scripts/05_generate_league_team_details.py
Genera los JSONs de detalle por equipo para La Liga, Bundesliga, Serie A y Ligue 1.

Fuentes:
  - data/raw/{liga}_understat_players.csv → squad (Understat)
  - data/raw/players_data-2025_2026.csv   → posiciones y nacionalidades (FBref)
  - data/processed/{liga}_splits.json     → stats de equipo (W/D/L, xG, etc.)
  - data/raw/games.csv                    → partidos (Transfermarkt)

NO requiere internet. Ejecutar: python scripts/05_generate_league_team_details.py
"""
import csv, json, os, unicodedata, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "data", "raw")
OUT  = os.path.join(BASE, "data", "processed")

# ── Normalización ─────────────────────────────────────────────────────────────
_SPECIAL = str.maketrans({
    'ø':'o','Ø':'o','ð':'d','Ð':'d','þ':'th','Þ':'th','ß':'ss',
    'æ':'ae','Æ':'ae','ł':'l','Ł':'l','đ':'d','Đ':'d','œ':'oe','Œ':'oe',
})
def norm(s):
    s = (s or '').translate(_SPECIAL)
    nfkd = unicodedata.normalize('NFD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn').lower().strip()

# ── Posición FBref (mejorada) ─────────────────────────────────────────────────
# Regla: si alguno de los códigos es FW → delantero (cubre a extremos/mediapuntas)
# Ejemplos: "MF,FW" → F (Yamal, Raphinha), "FW,MF" → F, "DF,MF" → D
def fbref_pos(pos_str):
    p = (pos_str or '').upper().strip()
    codes = [c.strip() for c in p.split(',')]
    if 'GK' in codes:  return 'G'
    if 'FW' in codes:  return 'F'   # cualquier combinación con FW → delantero
    if codes[0] == 'DF': return 'D'
    if codes[0] == 'MF': return 'M'
    return 'M'

# ── Nacionalidad FBref ────────────────────────────────────────────────────────
# "gb-eng ENG" → ('GB-ENG', 'England')   /   "es ESP" → ('ES', 'Spain')
COUNTRY_NAMES = {
    'ESP':'Spain','FRA':'France','GER':'Germany','ITA':'Italy','POR':'Portugal',
    'NED':'Netherlands','BEL':'Belgium','ENG':'England','SCO':'Scotland',
    'WAL':'Wales','NIR':'N. Ireland','IRL':'Ireland','BRA':'Brazil','ARG':'Argentina',
    'COL':'Colombia','URU':'Uruguay','CHI':'Chile','ECU':'Ecuador','MEX':'Mexico',
    'CRC':'Costa Rica','USA':'USA','CAN':'Canada','SEN':'Senegal','NGA':'Nigeria',
    'GHA':'Ghana','CIV':"Ivory Coast",'CMR':'Cameroon','MAR':'Morocco','TUN':'Tunisia',
    'ALG':'Algeria','EGY':'Egypt','MLI':'Mali','SWE':'Sweden','NOR':'Norway',
    'DEN':'Denmark','FIN':'Finland','ISL':'Iceland','AUT':'Austria','SUI':'Switzerland',
    'POL':'Poland','CRO':'Croatia','SRB':'Serbia','CZE':'Czechia','SVK':'Slovakia',
    'HUN':'Hungary','ROM':'Romania','BUL':'Bulgaria','GRE':'Greece','TUR':'Turkey',
    'RUS':'Russia','UKR':'Ukraine','GEO':'Georgia','ARM':'Armenia','ALB':'Albania',
    'KOS':'Kosovo','MNE':'Montenegro','MKD':'N. Macedonia','KOR':'South Korea',
    'JPN':'Japan','ISR':'Israel','AUS':'Australia','BOL':'Bolivia','PAR':'Paraguay',
    'PER':'Peru','VEN':'Venezuela','GUY':'Guyana','HAI':'Haiti','JAM':'Jamaica',
    'TRI':'Trinidad & Tobago','BFA':'Burkina Faso','GUI':'Guinea','GAB':'Gabon',
    'BEN':'Benin','TOG':'Togo','BIH':'Bosnia','SVN':'Slovenia','LAT':'Latvia',
    'EST':'Estonia','LTU':'Lithuania','KAZ':'Kazakhstan','LUX':'Luxembourg',
    'MON':'Monaco','CPV':'Cape Verde','GUB':'Guinea-Bissau','MOZ':'Mozambique',
    'ZIM':'Zimbabwe','COD':'DR Congo','CGO':'Congo','ANG':'Angola','MRI':'Mauritius',
    'COM':'Comoros','NZL':'New Zealand','CHN':'China','IRN':'Iran','SAU':'Saudi Arabia',
    'NGA':'Nigeria',
}
IOC_TO_ISO = {
    'gb-eng':'GB-ENG','gb-sct':'GB-SCT','gb-wls':'GB-WLS','gb-nir':'GB-NIR',
    'kor':'KR','cro':'HR','ned':'NL','por':'PT','ger':'DE','sui':'CH',
    'bra':'BR','arg':'AR','chi':'CL','col':'CO','uru':'UY','ecu':'EC',
    'bol':'BO','par':'PY','ven':'VE','per':'PE','civ':'CI','nga':'NG',
    'sen':'SN','gha':'GH','cmr':'CM','cgo':'CG','cod':'CD','mar':'MA',
    'tun':'TN','alg':'DZ','egy':'EG','mli':'ML','bfa':'BF','gui':'GN',
    'guy':'GY','sur':'SR','hai':'HT','mex':'MX','cos':'CR','hon':'HN',
    'jam':'JM','tri':'TT','cub':'CU','irl':'IE','usa':'US','can':'CA',
    'aus':'AU','nzl':'NZ','jpn':'JP','chn':'CN','tur':'TR','gre':'GR',
    'srb':'RS','bih':'BA','svk':'SK','svn':'SI','lat':'LV','est':'EE',
    'lit':'LT','isr':'IL','geo':'GE','arm':'AM','kaz':'KZ','isl':'IS',
    'fin':'FI','nor':'NO','swe':'SE','den':'DK','aut':'AT','bel':'BE',
    'pol':'PL','rom':'RO','bul':'BG','hun':'HU','cze':'CZ','alb':'AL',
    'mne':'ME','mkd':'MK','kos':'XK','mon':'MC','lux':'LU','gab':'GA',
    'ben':'BJ','tog':'TG','cpv':'CV','moz':'MZ','zim':'ZW','ang':'AO',
    'com':'KM','mri':'MU','sau':'SA',
}
def parse_nation(nat):
    if not nat or not nat.strip():
        return '', ''
    parts = nat.strip().split()
    if len(parts) < 2:
        return '', ''
    ioc = parts[0].lower()
    code3 = parts[1].upper()
    if len(ioc) == 2 and '-' not in ioc:
        iso = ioc.upper()
    else:
        iso = IOC_TO_ISO.get(ioc, ioc.upper()[:2])
    return iso, COUNTRY_NAMES.get(code3, code3)

# ── Configuración por liga ────────────────────────────────────────────────────
# splits_name → [understat_csv_name, fbref_squad_name, transfermarkt_name]
LEAGUES = {
    'laliga': {
        'splits':    'laliga_splits.json',
        'understat': 'laliga_understat_players.csv',
        'fbref_comp':'es La Liga',
        'games_comp':'ES1',
        'teams': {
            'FC Barcelona':              ('Barcelona',      'Barcelona',      'Futbol Club Barcelona'),
            'Real Madrid':               ('Real Madrid',    'Real Madrid',    'Real Madrid Club de Fútbol'),
            'Villarreal CF':             ('Villarreal',     'Villarreal',     'Villarreal Club de Fútbol S.A.D.'),
            'Atlético de Madrid':        ('Atletico Madrid','Atlético Madrid','Club Atlético de Madrid S.A.D.'),
            'Real Betis':                ('Real Betis',     'Real Betis',     'Real Betis Balompié S.A.D.'),
            'Celta':                     ('Celta Vigo',     'Celta Vigo',     'Real Club Celta de Vigo S. A. D.'),
            'Getafe CF':                 ('Getafe',         'Getafe',         'Getafe Club de Fútbol S. A. D. Team Dubai'),
            'Rayo Vallecano':            ('Rayo Vallecano', 'Rayo Vallecano', 'Rayo Vallecano de Madrid S. A. D.'),
            'Valencia CF':               ('Valencia',       'Valencia',       'Valencia Club de Fútbol S. A. D.'),
            'Real Sociedad':             ('Real Sociedad',  'Real Sociedad',  'Real Sociedad de Fútbol S.A.D.'),
            'RCD Espanyol de Barcelona': ('Espanyol',       'Espanyol',       'Reial Club Deportiu Espanyol de Barcelona S.A.D.'),
            'Athletic Club':             ('Athletic Club',  'Athletic Club',  'Athletic Club Bilbao'),
            'Elche CF':                  ('Elche',          'Elche',          'Elche Club de Fútbol S.A.D.'),
            'Deportivo Alavés':          ('Alaves',         'Alavés',         'Deportivo Alavés S. A. D.'),
            'Sevilla FC':                ('Sevilla',        'Sevilla',        'Sevilla Fútbol Club S.A.D.'),
            'CA Osasuna':                ('Osasuna',        'Osasuna',        'Club Atlético Osasuna'),
            'RCD Mallorca':              ('Mallorca',       'Mallorca',       'Real Club Deportivo Mallorca S.A.D.'),
            'Levante UD':                ('Levante',        'Levante',        'Levante Unión Deportiva S.A.D.'),
            'Girona FC':                 ('Girona',         'Girona',         'Girona Fútbol Club S. A. D.'),
            'Real Oviedo':               ('Real Oviedo',    'Oviedo',         'Real Oviedo S.A.D.'),
        }
    },
    'bundesliga': {
        'splits':    'bundesliga_splits.json',
        'understat': None,  # sin CSV Understat → usar FBref
        'fbref_comp':'de Bundesliga',
        'games_comp':'L1',
        'teams': {
            'Bayern München':           (None, 'Bayern Munich',     'FC Bayern München'),
            'Borussia Dortmund':        (None, 'Dortmund',          'Borussia Dortmund'),
            'RB Leipzig':               (None, 'RB Leipzig',        'RasenBallsport Leipzig'),
            'VfB Stuttgart':            (None, 'Stuttgart',         'Verein für Bewegungsspiele Stuttgart 1893'),
            'TSG Hoffenheim':           (None, 'Hoffenheim',        'Turn- und Sportgemeinschaft 1899 Hoffenheim Fußball-Spielbetriebs'),
            'Bayer 04 Leverkusen':      (None, 'Leverkusen',        'Bayer 04 Leverkusen Fußball'),
            'SC Freiburg':              (None, 'Freiburg',          'Sport-Club Freiburg'),
            'Eintracht Frankfurt':      (None, 'Eintracht Frankfurt','Eintracht Frankfurt Fußball AG'),
            'FC Augsburg':              (None, 'Augsburg',          'Fußball-Club Augsburg 1907'),
            '1. FSV Mainz 05':          (None, 'Mainz 05',          '1. Fußball- und Sportverein Mainz 05'),
            '1. FC Union Berlin':       (None, 'Union Berlin',      '1. Fußballclub Union Berlin'),
            'Borussia Mönchengladbach': (None, 'Gladbach',          'Borussia Verein für Leibesübungen 1900 Mönchengladbach'),
            'Hamburger SV':             (None, 'Hamburger SV',      'Hamburger Sport Verein'),
            '1. FC Köln':               (None, 'Köln',              '1. Fußball-Club Köln'),
            'Werder Bremen':            (None, 'Werder Bremen',     'Sportverein Werder Bremen von 1899'),
            'VfL Wolfsburg':            (None, 'Wolfsburg',         'Verein für Leibesübungen Wolfsburg'),
            'FC Heidenheim 1846':       (None, 'Heidenheim',        '1. Fußballclub Heidenheim 1846'),
            'FC St. Pauli':             (None, 'St Pauli',          'Fußball-Club St. Pauli von 1910'),
        }
    },
    'seriea': {
        'splits':    'seriea_splits.json',
        'understat': 'seriea_understat_players.csv',
        'fbref_comp':'it Serie A',
        'games_comp':'IT1',
        'teams': {
            'FC Internazionale': ('Inter',           'Inter',       'Football Club Internazionale Milano S.p.A.'),
            'SSC Napoli':        ('Napoli',          'Napoli',      'Società Sportiva Calcio Napoli'),
            'AS Roma':           ('Roma',            'Roma',        'Associazione Sportiva Roma'),
            'Como 1907':         ('Como',            'Como',        'Calcio Como'),
            'AC Milan':          ('AC Milan',        'Milan',       'Associazione Calcio Milan'),
            'Juventus':          ('Juventus',        'Juventus',    'Juventus Football Club'),
            'Atalanta BC':       ('Atalanta',        'Atalanta',    'Atalanta Bergamasca Calcio S.p.a.'),
            'Bologna FC':        ('Bologna',         'Bologna',     'Bologna Football Club 1909'),
            'SS Lazio':          ('Lazio',           'Lazio',       'Società Sportiva Lazio S.p.A.'),
            'Udinese Calcio':    ('Udinese',         'Udinese',     'Udinese Calcio'),
            'US Sassuolo':       ('Sassuolo',        'Sassuolo',    'Unione Sportiva Sassuolo Calcio'),
            'Parma Calcio':      ('Parma Calcio 1913','Parma',      'Parma Calcio 1913'),
            'Torino FC':         ('Torino',          'Torino',      'Torino Calcio'),
            'Cagliari Calcio':   ('Cagliari',        'Cagliari',    'Cagliari Calcio'),
            'ACF Fiorentina':    ('Fiorentina',      'Fiorentina',  'Associazione Calcio Fiorentina'),
            'Genoa CFC':         ('Genoa',           'Genoa',       'Genoa Cricket and Football Club'),
            'US Lecce':          ('Lecce',           'Lecce',       'Unione Sportiva Lecce'),
            'US Cremonese':      ('Cremonese',       'Cremonese',   'Unione Sportiva Cremonese S.p.A.'),
            'Hellas Verona':     ('Verona',          'Hellas Verona','Verona Hellas Football Club'),
            'AC Pisa':           ('Pisa',            'Pisa',        'Pisa Sporting Club'),
        }
    },
    'ligue1': {
        'splits':    'ligue1_splits.json',
        'understat': 'ligue1_understat_players.csv',
        'fbref_comp':'fr Ligue 1',
        'games_comp':'FR1',
        'teams': {
            'Paris Saint-Germain':   ('Paris Saint Germain','Paris Saint-Germain',"Paris Saint-Germain Football Club"),
            'RC Lens':               ('Lens',         'Lens',          'Racing Club de Lens'),
            'LOSC Lille':            ('Lille',        'Lille',         'Lille Olympique Sporting Club'),
            'Olympique Lyonnais':    ('Lyon',         'Lyon',          'Olympique Lyonnais'),
            'Olympique de Marseille':('Marseille',    'Marseille',     'Olympique de Marseille'),
            'Stade Rennais':         ('Rennes',       'Rennes',        'Stade Rennais Football Club'),
            'AS Monaco':             ('Monaco',       'Monaco',        'Association sportive de Monaco Football Club'),
            'RC Strasbourg':         ('Strasbourg',   'Strasbourg',    'Racing Club de Strasbourg Alsace'),
            'FC Lorient':            ('Lorient',      'Lorient',       'Football Club Lorient-Bretagne Sud'),
            'Toulouse FC':           ('Toulouse',     'Toulouse',      'Toulouse Football Club'),
            'Paris FC':              ('Paris FC',     'Paris FC',      'Paris Football Club'),
            'Stade Brestois 29':     ('Brest',        'Brest',         'Stade brestois 29'),
            'Angers SCO':            ('Angers',       'Angers',        "Angers Sporting Club de l'Ouest"),
            'Le Havre AC':           ('Le Havre',     'Le Havre',      'Le Havre Athletic Club'),
            'AJ Auxerre':            ('Auxerre',      'Auxerre',       'Association de la Jeunesse auxerroise'),
            'OGC Nice':              ('Nice',         'Nice',          "Olympique Gymnaste Club Nice Côte d'Azur"),
            'FC Nantes':             ('Nantes',       'Nantes',        'Football Club de Nantes'),
            'FC Metz':               ('Metz',         'Metz',          'Football Club de Metz'),
        }
    },
}

# ── Leer FBref (posiciones y nacionalidades) ──────────────────────────────────
print("Cargando FBref…")
fbref_by_comp = {}  # {comp: {norm_name: {pos, flag, country}}}
with open(os.path.join(RAW, 'players_data-2025_2026.csv'), encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        comp = row['Comp']
        if comp not in fbref_by_comp:
            fbref_by_comp[comp] = {}
        iso, country = parse_nation(row.get('Nation',''))
        primary_pos = fbref_pos(row.get('Pos',''))
        key = norm(row['Player'])
        mins = int(row.get('Min', 0) or 0)
        # Guardar el que más minutos tiene si hay duplicado
        existing = fbref_by_comp[comp].get(key)
        if existing is None or mins > existing.get('min', 0):
            fbref_by_comp[comp][key] = {
                'pos':     primary_pos,
                'flag':    iso,
                'country': country,
                'squad':   row.get('Squad',''),
                'min':     mins,
            }
print(f"  {sum(len(v) for v in fbref_by_comp.values())} jugadores FBref en {len(fbref_by_comp)} ligas")

# ── Leer games.csv (partidos) ─────────────────────────────────────────────────
print("Cargando partidos (games.csv)…")
games_raw = []
with open(os.path.join(RAW, 'games.csv'), encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('season') == '2025' and row.get('competition_type') == 'domestic_league':
            games_raw.append(row)
print(f"  {len(games_raw)} partidos domésticos 2025/26")

# ── Helpers de matching ───────────────────────────────────────────────────────
def find_fbref(player_name, fbref_idx):
    n = norm(player_name)
    if n in fbref_idx:
        return fbref_idx[n]
    last = n.split()[-1] if n.split() else ''
    if len(last) >= 4:
        matches = [v for k, v in fbref_idx.items() if k.endswith(' ' + last)]
        if len(matches) == 1:
            return matches[0]
    first = n.split()[0] if n.split() else ''
    if len(first) >= 4:
        matches = [v for k, v in fbref_idx.items() if k.startswith(first + ' ') or k == first]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            valid = [m for m in matches if m.get('min', 0) > 100]
            if valid:
                return max(valid, key=lambda x: x['min'])
    return None

POS_ORDER = {'G': 0, 'D': 1, 'M': 2, 'F': 3}

# ── Generar JSONs ─────────────────────────────────────────────────────────────
for league_key, cfg in LEAGUES.items():
    print(f"\n{'='*50}")
    print(f"Procesando {league_key.upper()}…")

    # 1. Splits
    with open(os.path.join(OUT, cfg['splits']), encoding='utf-8') as f:
        splits = json.load(f)
    splits_by_team = {t['team']: t for t in splits['total']}

    # 2. Understat players (squad source)
    understat_by_team = {}
    if cfg['understat']:
        csv_path = os.path.join(RAW, cfg['understat'])
        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                mins = int(row.get('min', 0) or 0)
                apps = int(row.get('apps', 0) or 0)
                if mins == 0 and apps == 0:
                    continue
                primary_team = row['team'].split(',')[0].strip()
                if primary_team not in understat_by_team:
                    understat_by_team[primary_team] = []
                understat_by_team[primary_team].append({
                    'name':    row['player'].strip(),
                    'apps':    apps,
                    'min':     mins,
                    'goals':   int(float(row.get('goals', 0) or 0)),
                    'assists': int(float(row.get('a', 0) or 0)),
                    'xG':      round(float(row.get('xG', 0) or 0), 2),
                    'xA':      round(float(row.get('xA', 0) or 0), 2),
                })

    # 3. FBref index para esta liga
    fbref_idx = fbref_by_comp.get(cfg['fbref_comp'], {})
    # También indice por squad
    fbref_by_squad = {}
    for k, v in fbref_idx.items():
        sq = v.get('squad', '')
        if sq not in fbref_by_squad:
            fbref_by_squad[sq] = {}
        fbref_by_squad[sq][k] = v

    # 4. Partidos
    comp_games = [g for g in games_raw if g['competition_id'] == cfg['games_comp']]
    # Índice de partidos por nombre Transfermarkt
    def build_matches(tm_name):
        ms = []
        for g in comp_games:
            home = g['home_club_name']
            away = g['away_club_name']
            if home != tm_name and away != tm_name:
                continue
            hg = int(g['home_club_goals'] or 0)
            ag = int(g['away_club_goals'] or 0)
            is_home = home == tm_name
            opp = away if is_home else home
            gf = hg if is_home else ag
            ga = ag if is_home else hg
            if gf > ga:   result = 'W'
            elif gf < ga: result = 'L'
            else:         result = 'D'
            ms.append({
                'date':    g['date'],
                'round':   g['round'],
                'home':    home,
                'away':    away,
                'homeScore': hg,
                'awayScore': ag,
                'isHome':  is_home,
                'opponent':opp,
                'gf':      gf,
                'ga':      ga,
                'result':  result,
            })
        ms.sort(key=lambda x: x['date'])
        return ms

    # 5. Construir datos por equipo
    all_teams = {}
    for splits_name, (understat_name, fbref_name, tm_name) in cfg['teams'].items():
        s = splits_by_team.get(splits_name, {})
        wins   = s.get('wins', 0)
        draws  = s.get('draws', 0)
        losses = s.get('loses', 0)
        gf     = s.get('scored', 0)
        gc     = s.get('missed', 0)
        xG     = round(s.get('xG', 0) or 0, 2)
        npxG   = round(s.get('npxG', 0) or 0, 2)
        xGA    = round(s.get('xGA', 0) or 0, 2)
        xPTS   = round(s.get('xPTS', 0) or 0, 2)
        pts    = s.get('pts', 0)

        # Stats array
        stats = [
            {'key':'wins',   'label':'Victorias',          'value': wins},
            {'key':'draws',  'label':'Empates',             'value': draws},
            {'key':'losses', 'label':'Derrotas',            'value': losses},
            {'key':'gf',     'label':'Goles marcados',      'value': gf},
            {'key':'gc',     'label':'Goles encajados',     'value': gc},
            {'key':'gd',     'label':'Diferencia de goles', 'value': gf - gc},
            {'key':'pts',    'label':'Puntos',              'value': pts},
            {'key':'xG',     'label':'xG',                  'value': xG},
            {'key':'npxG',   'label':'npxG (sin penaltis)', 'value': npxG},
            {'key':'xGA',    'label':'xGA',                 'value': xGA},
            {'key':'xPTS',   'label':'xPTS',                'value': xPTS},
        ]

        # Squad — Understat o FBref
        squad = []
        fbref_squad_idx = fbref_by_squad.get(fbref_name, {})

        if understat_name and understat_name in understat_by_team:
            for p in understat_by_team[understat_name]:
                fb = find_fbref(p['name'], fbref_squad_idx) or find_fbref(p['name'], fbref_idx)
                squad.append({
                    'name':     p['name'],
                    'position': fb['pos'] if fb else 'M',
                    'games':    p['apps'],
                    'goals':    p['goals'],
                    'assists':  p['assists'],
                    'minutes':  p['min'],
                    'xG':       p['xG'],
                    'xA':       p['xA'],
                    'flag':     fb['flag']    if fb else '',
                    'country':  fb['country'] if fb else '',
                })
        else:
            # Bundesliga: usar FBref directamente
            for k, fb in fbref_squad_idx.items():
                if fb.get('min', 0) == 0:
                    continue
                squad.append({
                    'name':     k,  # nombre normalizado — mejor usar el original
                    'position': fb['pos'],
                    'games':    0,
                    'goals':    0,
                    'assists':  0,
                    'minutes':  fb['min'],
                    'xG':       0,
                    'xA':       0,
                    'flag':     fb['flag'],
                    'country':  fb['country'],
                })

        # Para Bundesliga: recuperar nombre original del FBref
        if not understat_name:
            # Re-leer con nombres originales
            squad = []
            with open(os.path.join(RAW, 'players_data-2025_2026.csv'), encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    if row['Comp'] != cfg['fbref_comp']:
                        continue
                    if row.get('Squad','') != fbref_name:
                        continue
                    mins = int(row.get('Min', 0) or 0)
                    if mins == 0:
                        continue
                    iso, country = parse_nation(row.get('Nation',''))
                    squad.append({
                        'name':     row['Player'],
                        'position': fbref_pos(row.get('Pos','')),
                        'games':    int(row.get('MP', 0) or 0),
                        'goals':    int(row.get('Gls', 0) or 0),
                        'assists':  int(row.get('Ast', 0) or 0),
                        'minutes':  mins,
                        'xG':       0,
                        'xA':       0,
                        'flag':     iso,
                        'country':  country,
                    })

        squad.sort(key=lambda x: (POS_ORDER.get(x['position'], 4), -x['minutes']))

        # Agregar stats de equipo desde squad
        team_goals   = sum(p['goals']   for p in squad)
        team_assists = sum(p['assists'] for p in squad)
        team_xG_sum  = round(sum(p.get('xG', 0) for p in squad), 2)
        if team_goals > 0:
            stats.append({'key':'player_goals',   'label':'Goles (jugadores)', 'value': team_goals})
            stats.append({'key':'player_assists',  'label':'Asistencias',       'value': team_assists})
        if team_xG_sum > 0:
            stats.append({'key':'player_xG',       'label':'xG (jugadores)',    'value': team_xG_sum})

        # Partidos
        matches = build_matches(tm_name)

        all_teams[splits_name] = {
            'name':    splits_name,
            'wins':    wins,
            'draws':   draws,
            'losses':  losses,
            'gf':      gf,
            'gc':      gc,
            'xG':      xG,
            'xGA':     xGA,
            'xPTS':    xPTS,
            'pts':     pts,
            'squad':   squad,
            'stats':   stats,
            'matches': matches,
        }
        print(f"  {splits_name}: {len(squad)} jugadores, {len(matches)} partidos")

    # Guardar
    out_path = os.path.join(OUT, f'{league_key}_team_details.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'league': league_key, 'season': '2025/26', 'teams': all_teams},
                  f, ensure_ascii=False)
    print(f"✅ {league_key}_team_details.json guardado ({len(all_teams)} equipos)")

print("\n✅ Todos los JSONs generados.")
print("Reinicia el servidor (python app.py) y recarga http://localhost:8080")

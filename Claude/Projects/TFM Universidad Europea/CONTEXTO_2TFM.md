# CONTEXTO_2TFM — FC Barcelona Analytics Dashboard
> Documento de estado para continuación del proyecto. Generado: junio 2026.
> **Este documento reemplaza a `CONTEXTO_TFM.md` (fase 1). Léelo completo antes de hacer cualquier cambio.**

---

## 1. IDENTIFICACIÓN DEL PROYECTO

**Título TFM:** Análisis de Big Data Deportivo — FC Barcelona Analytics Department  
**Institución:** Universidad Europea  
**Ruta del proyecto:** `/Users/rodrigo/Documents/Claude/Projects/TFM Universidad Europea/barca-dashboard/`  
**Puerto local:** http://localhost:8080  
**Email usuario:** rm386196@gmail.com

### Arrancar el servidor
```bash
cd "/Users/rodrigo/Documents/Claude/Projects/TFM Universidad Europea/barca-dashboard"
source venv/bin/activate
python app.py
# Abrir: http://localhost:8080
```

---

## 2. ARQUITECTURA TÉCNICA

- **Backend:** Python 3 + Flask (puerto 8080)
- **Frontend:** HTML5 + Vanilla JS + Chart.js 4.4.0 — SPA en `templates/index.html` (~5000+ líneas)
- **Datos:** JSON estáticos en `data/processed/` servidos por Flask
- **Sin base de datos**

### Scripts disponibles
| Script | Función |
|--------|---------|
| `scripts/01_process_data.py` | Procesa Kaggle CSVs + Understat CSVs → JSONs (todas las ligas) |
| `scripts/02_fetch_understat.py` | Scraping Understat (con protección anti-borrado) |
| `scripts/03_fetch_epl_detail.py` | Fetch Premier League API oficial → `epl_teams_detail.json` (ejecutar en Mac con internet) |

---

## 3. RUTAS API COMPLETAS (app.py)

### FC Barcelona
```
GET /api/barca/games              → Todos los partidos del Barça
GET /api/barca/matches/understat  → Partidos con xG
GET /api/barca/champions          → Partidos UCL
GET /api/barca/copadelrey         → Partidos Copa del Rey
GET /api/barca/supercopa          → Partidos Supercopa
GET /api/barca/players            → Jugadores FBref
GET /api/barca/players/understat  → Jugadores Understat xG/xA
GET /api/barca/players/advanced   → Stats avanzadas
GET /api/barca/transfers          → Transferencias
GET /api/barca/valuations         → Valoraciones mercado
GET /api/barca/squad-value-history → Evolución valor plantilla
```

### La Liga
```
GET /api/laliga/splits      → Tabla total/local/visitante con xG/xGA/xPTS
GET /api/laliga/players     → 600 jugadores Understat
GET /api/laliga/progression → Puntos acumulados 38 JJ
```

### Premier League (EPL)
```
GET /api/epl/splits         → Tabla total/local/visitante con xG/xGA/xPTS
GET /api/epl/players        → 537 jugadores Understat
GET /api/epl/progression    → Puntos acumulados 38 JJ
GET /api/epl/table          → Tabla completa (backup)
GET /api/epl/teams/detail   → Detalle por equipo (plantilla, stats, partidos, estadio)
```

### Bundesliga
```
GET /api/bundesliga/splits      → Tabla total/local/visitante
GET /api/bundesliga/players     → 507 jugadores FBref
GET /api/bundesliga/progression → Puntos acumulados 34 JJ
```

### Serie A
```
GET /api/seriea/splits      → Tabla total/local/visitante
GET /api/seriea/players     → 586 jugadores Understat
GET /api/seriea/progression → Puntos acumulados 38 JJ
```

### Ligue 1
```
GET /api/ligue1/splits      → Tabla total/local/visitante
GET /api/ligue1/players     → 553 jugadores Understat
GET /api/ligue1/progression → Puntos acumulados 34 JJ
```

### Otras ligas / general
```
GET /api/ucl/table          → UCL 36 equipos
GET /api/uel/table          → UEL 36 equipos
GET /api/leagues/tables     → 5 ligas Kaggle (compatibilidad)
GET /api/leagues/players    → FBref todos los jugadores
GET /api/status             → Estado de archivos de datos
```

---

## 4. FUENTES DE DATOS POR LIGA

| Liga | Tabla | Jugadores | Progresión | Notas |
|------|-------|-----------|-----------|-------|
| La Liga | `laliga_understat_table.csv` + home/away | `laliga_understat_players.csv` | Kaggle ES1 (34JJ) + interpol. a 38 | Understat 38 PJ completas |
| Premier League | `epl_understat_table.csv` + home/away | `epl_understat_players.csv` | Kaggle GB1 (35JJ) + interpol. a 38 | Understat 38 PJ completas |
| Bundesliga | `bundesliga_understat_table.csv` + home/away | `players_data-2025_2026.csv` FBref | Kaggle L1 (32JJ) + interpol. a 34 | Jugadores de FBref, no Understat |
| Serie A | `seriea_understat_table.csv` + home/away | `seriea_understat_players.csv` | Kaggle IT1 (35JJ) + interpol. a 38 | Understat 38 PJ completas |
| Ligue 1 | `ligue1_understat_table.csv` + home/away | `ligue1_understat_players.csv` | Kaggle FR1 (32JJ) + interpol. a 34 | Ligue 1 = 18 equipos, 34 JJ |
| EPL Detail | API PL oficial (temporada 777) | API PL oficial | — | Script `03_fetch_epl_detail.py` |

---

## 5. ESTADO DE CADA SECCIÓN — COMPLETO

### PORTADA (Hero)
- **Estado:** ✅ Terminada
- 8 tarjetas de ligas en grid 4+4, fondo blanco
- Logo LaLiga: `/static/img/laliga.png` (el original del CONTEXTO_TFM.md)
- Tarjeta LaLiga tiene fondo blanco como las demás
- Botón "Entrar al Dashboard del Barça"

### DASHBOARD FC BARCELONA
- **Estado:** ✅ Terminado (sin cambios en esta fase)
- Equipo, Partidos, Jugadores, Champions, Copa & Supercopa, Stats Avanzadas, Plantilla & Mercado, Comparativa Europa

---

### LA LIGA EA SPORTS
- **Estado:** ✅ Terminada y completa
- **Hero:** fondo rojo `#EE3524` completo, "LaLiga" blanco + "Temporada 2025/26 · España" — sin recuadros
- **Tabla:** escudos api-sports.io, columnas xPTS coloreadas (verde si Pts>xPTS, rojo si Pts<xPTS)
- **Filtro:** Partidos totales / Local / Visitante — selector borde rojo
- **KPIs:** Campeón, Máx. GF (equipo), Mayor xG, Menor xGA — orden: título→logo→número→métrica→equipo
- **TOP RENDIMIENTO:** Mbappé (goleador+G+A), Yamal (asistente), Radu (minutos)
  - Fotos: `laliga_mbappe.png`, `laliga_yamal.png`, `laliga_radu.png` ✅ guardadas
- **Gráfico:** Progresión 38 JJ, leyenda derecha con nombre equipos, colores distintos
- **Escudos corregidos:** Elche=`/static/img/elche.svg`, Alavés=`/static/img/alaves.svg`, Levante=`/static/img/levante.svg`, Oviedo=`/static/img/oviedo.svg`, Girona=api-sports/547

### PREMIER LEAGUE
- **Estado:** ✅ Terminada + funcionalidad de detalle por equipo implementada
- **Hero:** gradiente morado `#3d195b→#5c2d8b`, "Premier League" blanco
- **Tabla:** escudos api-sports.io, xPTS coloreado, filtro total/local/visitante
- **KPIs:** Campeón, Equipo Goleador, Mayor xG, Menor xGA
- **TOP RENDIMIENTO:** Haaland (gol+G+A), Bruno Fernandes (asistente), Van Dijk (minutos)
  - Fotos: `epl_haaland.jpg`, `epl_brunofernandes.jpg`, `epl_vandijk.jpg` ✅ guardadas
- **Gráfico:** 38 JJ, leyenda blanca, Arsenal resaltado
- **Detalle por equipo (EPL Team Detail):** 
  - Nombres de equipo en tabla son **clickables** (subrayado punteado)
  - Abre overlay lateral con 4 tabs: Estadio, Plantilla, Estadísticas, Partidos
  - Datos desde `epl_teams_detail.json` (generado por `03_fetch_epl_detail.py`)
  - API PL oficial temporada 777 (2025/26)
  - ⚠️ **PENDIENTE DE MODIFICACIONES** — ver sección 7

### BUNDESLIGA
- **Estado:** ✅ Terminada
- **Hero:** gradiente rojo `#d20515→#a00010`, "Bundesliga" blanco — sin logo, sin bandera 🇩🇪
- **Tabla:** escudos api-sports.io, xPTS coloreado, filtro total/local/visitante, color `#d20515`
- **KPIs:** Campeón, Equipo Goleador, Mayor xG, Menor xGA
- **TOP RENDIMIENTO:** Kane (gol+G+A), Olise (asistente), Atubolu (minutos)
  - Fotos: `bundesliga_kane.jpg`, `bundesliga_olise.jpg`, `bundesliga_atubolu.jpg` ✅ guardadas
- **Gráfico:** 34 JJ, leyenda blanca, Bayern resaltado

### SERIE A
- **Estado:** ✅ Terminada
- **Hero:** gradiente azul `#024494→#001f6b`, "Serie A" blanco — sin logo, sin bandera 🇮🇹
- **Tabla:** escudos api-sports.io, xPTS coloreado, filtro total/local/visitante, color `#024494`
- **KPIs:** Campeón, Equipo Goleador, Mayor xG, Menor xGA
- **TOP RENDIMIENTO:** Lautaro (gol+G+A), Dimarco (asistente), Falcone (minutos)
  - Fotos: `seriea_lautaro.jpg`, `seriea_dimarco.jpg`, `seriea_falcone.jpg` ✅ guardadas
  - Sort de minutos: `sort((a,b) => b.min - a.min)` — Falcone sale primero
- **Gráfico:** 38 JJ, leyenda blanca, Inter resaltado
- **Fotos plantilla dict:** `SERIEA_PLAYER_PHOTOS` con rutas locales + fallback Wikipedia

### LIGUE 1
- **Estado:** ✅ Terminada
- **Hero:** gradiente azul oscuro `#091c3e→#1a3a6e`, "Ligue 1" blanco — sin logo, sin bandera 🇫🇷, sin "McDonald's"
- **Tabla:** escudos api-sports.io, xPTS coloreado, filtro total/local/visitante, color `#1a3a6e`
- **KPIs:** Campeón (PSG 76pts), Equipo Goleador, Mayor xG, Menor xGA
- **TOP RENDIMIENTO:** Lepaul/Rennes (gol+G+A), Ajorque/Brest (asistente), Lefort/Angers (minutos)
  - Fotos: `ligue1_lepaul.jpg`, `ligue1_ajorque.jpg`, `ligue1_lefort.jpg` ✅ guardadas
- **Gráfico:** 34 JJ, leyenda blanca, PSG resaltado
- **Títulos de sección:** CLASIFICACIÓN, TOP RENDIMIENTO 2025/26, EVOLUCIÓN DE PUNTOS POR JORNADA en **blanco** (ajustado por petición del usuario)
- **Jugadores multi-equipo:** `team = row['team'].split(',')[0].strip()` — usa el primer equipo

### UCL / UEL
- **Estado:** ✅ Terminadas (sin cambios en esta fase)
- Tabla general 36 equipos, KPIs, buscador, zonas de clasificación

### LIGA PORTUGAL
- **Estado:** ⚠️ Datos limitados (sin Understat, solo Kaggle)

---

## 6. CONVENCIONES ACORDADAS (NO CAMBIAR)

### Diseño
- **Fondo:** `#0d1117` (dark mode)
- **Cards:** `#161b22`
- **Puerto:** siempre 8080
- **Sin emojis** en títulos de sección ni en las cards
- **Sin `localStorage`** en el frontend
- **Chart.js:** siempre `chart.destroy()` antes de crear nueva instancia

### Colores por liga
| Liga | Acento | Hero background |
|------|--------|----------------|
| La Liga | `#EE3524` | `background:#EE3524` sólido |
| Premier League | `#5c2d8b` | `linear-gradient(135deg,#3d195b,#5c2d8b)` |
| Bundesliga | `#d20515` | `linear-gradient(135deg,#d20515,#a00010)` |
| Serie A | `#024494` | `linear-gradient(135deg,#024494,#001f6b)` |
| Ligue 1 | `#1a3a6e` | `linear-gradient(135deg,#091c3e,#1a3a6e)` |
| UCL | — | `linear-gradient(135deg,#001a5e,#0a3d8f)` |
| UEL | — | `linear-gradient(135deg,#f05000,#b03000)` |
| Liga Portugal | — | `linear-gradient(135deg,#006600,#004400)` |

### KPI boxes — formato estándar (acordado)
```
TÍTULO (uppercase, color liga)
[Logo equipo 40px]
Número (grande, color liga)
métrica (muted, pequeño)
Nombre equipo (bold, pequeño)
```

### TOP RENDIMIENTO — formato estándar
- 4 cards: Máx. Goleador, Máx. Asistente, Más G+A, Más Minutos
- Foto en círculo 80px con fallback Wikipedia
- Valor en color liga, nombre jugador, nombre club
- Dict `LIGA_PLAYER_PHOTOS` con rutas `/static/img/liga_jugador.jpg`
- onerror: intenta local → Wikipedia → opacidad 0

### Tabla de clasificación — formato estándar
- Columnas: #, Equipo (con logo 22px), PJ, G, E, P, GF, GC, DG, Pts, xG, xGA, xPTS
- xPTS coloreado: `Pts > xPTS → verde`, `Pts < xPTS → rojo`, `igual → color liga`
- Filtro split total/local/visitante con dropdown borde color liga
- Zonas coloreadas con borde izquierdo: azul=Champions, naranja=Europa, verde=Conference, rojo=Descenso
- DG con signo `+/-` y color verde/rojo

### Gráfico de progresión — formato estándar
- Tipo: `line`, `TEAM_COLORS` (array de 20 colores)
- Leyenda derecha, `fontColor: '#e6edf3'` en cada item (CRÍTICO — sin esto las letras son oscuras)
- Tooltip: `Jornada X — Equipo: N pts`
- Equipo campeón con `borderWidth: 3` (resaltado)
- Etiqueta: `"${pts_finales} ${nombreEquipo}"` — permite saber pts al ver la leyenda

### Hero de página de liga — formato estándar
```html
<div class="lp-hero" style="background:[color]; flex-direction:column; align-items:flex-start; padding:18px 24px 14px;">
  <span style="font-family:'Arial Black',...; font-size:2.4rem; font-weight:900; color:#ffffff; ...">NombreLiga</span>
  <p style="color:rgba(255,255,255,0.85); font-size:0.88rem; margin-top:10px;">Temporada 2025/26 · País</p>
</div>
```
**Sin logo, sin bandera emoji, sin recuadros internos.**

### Nombres de escudos en tablas
- La Liga usa `LALIGA_MAP` con rutas api-sports.io o locales SVG
- EPL usa `EPL_MAP` + función `eplLogo(name, size)`
- Bundesliga usa `BUNDESLIGA_MAP` + función `buliLogo(name, size)`
- Serie A usa `SERIEA_MAP` + función `serieaLogo(name, size)`
- Ligue 1 usa `LIGUE1_MAP` + función `ligue1Logo(name, size)`

### Proceso de datos — pipeline estándar por liga
Todos los datos siguen este flujo:
1. CSVs Understat (table, home, away, players) → `data/raw/liga_understat_*.csv`
2. Script `01_process_data.py` → JSONs en `data/processed/`
3. Flask endpoints → Frontend JS

---

## 7. PENDIENTES INMEDIATOS (próxima sesión)

### EPL Team Detail — Overlay pendiente de modificaciones
El usuario solicitó cambios al overlay de detalle por equipo que **no se han implementado aún**:

1. **Cambiar panel lateral a página/panel independiente** (no slide lateral, sino vista nueva que reemplaza la página EPL o se abre centrada en toda la pantalla)

2. **Tab "ESTADIO" — Resumen Temporada:** Cambiar formato actual (número grande → letra pequeña debajo) por:
   ```
   VICTORIAS     EMPATES     DERROTAS
     [26]         [7]          [5]
   ```
   Y los 3 cards inferiores (Goles marcados, Goles encajados, Porterías a cero) con el mismo formato: **título en mayúsculas arriba, número grande abajo**.

3. **Tab "PLANTILLA":** Cambiar "27 jugadores en plantilla (primera plantilla)" por `JUGADORES PRIMER EQUIPO: 27`

4. **Tab "PLANTILLA" — Fotos de jugadores no se muestran.** El URL actual es:
   `https://resources.premierleague.com/premierleague/photos/players/250x250/p{playerId}.png`
   Verificar si las fotos cargan desde ese dominio en el navegador del usuario. Puede necesitar CORS o una URL diferente.

5. **Tab "ESTADÍSTICAS":** Cambiar formato a igual que "Resumen Temporada":
   - Sin emojis
   - Métrica en MAYÚSCULAS arriba
   - Número grande abajo
   - Mismo estilo visual de card

---

## 8. FOTOS DE JUGADORES — ESTADO COMPLETO

| Liga | Jugador | Archivo | Estado |
|------|---------|---------|--------|
| La Liga | Kylian Mbappé | `laliga_mbappe.png` | ✅ |
| La Liga | Lamine Yamal | `laliga_yamal.png` | ✅ |
| La Liga | Ionuț Radu | `laliga_radu.png` | ✅ |
| EPL | Erling Haaland | `epl_haaland.jpg` | ✅ |
| EPL | Bruno Fernandes | `epl_brunofernandes.jpg` | ✅ |
| EPL | Virgil van Dijk | `epl_vandijk.jpg` | ✅ |
| Bundesliga | Harry Kane | `bundesliga_kane.jpg` | ✅ |
| Bundesliga | Michael Olise | `bundesliga_olise.jpg` | ✅ |
| Bundesliga | Noah Atubolu | `bundesliga_atubolu.jpg` | ✅ |
| Serie A | Lautaro Martínez | `seriea_lautaro.jpg` | ✅ |
| Serie A | Federico Dimarco | `seriea_dimarco.jpg` | ✅ |
| Serie A | Wladimiro Falcone | `seriea_falcone.jpg` | ✅ |
| Ligue 1 | Esteban Lepaul | `ligue1_lepaul.jpg` | ✅ |
| Ligue 1 | Ludovic Ajorque | `ligue1_ajorque.jpg` | ✅ |
| Ligue 1 | Jordan Lefort | `ligue1_lefort.jpg` | ✅ |

---

## 9. EPL TEAM DETAIL — DATOS Y ESTRUCTURA

### JSON: `data/processed/epl_teams_detail.json`
```json
{
  "season": "2025/26",
  "teams": {
    "1": {  // PL API team ID (Arsenal=1, Man City=11, etc.)
      "team": { "id":1, "name":"Arsenal", "stadium":"Emirates Stadium", "city":"London", "capacity":60704 },
      "squad": [
        { "id":7975, "playerId":360351, "name":"David Raya", "shirt":1, "pos":"G",
          "posInfo":"Goalkeeper", "country":"Spain", "flag":"ES", "age":"30 years" }
      ],
      "stats": [
        { "key":"wins", "label":"Victorias", "value":26 }
      ],
      "matches": [
        { "id":124801, "gw":2, "date":"Sat 23 Aug 2025, 17:30 BST", "millis":1755966600000,
          "home":"Arsenal", "away":"Leeds United", "homeScore":5, "awayScore":0,
          "isHome":true, "opponent":"Leeds United", "gf":5, "ga":0, "result":"W" }
      ]
    }
  }
}
```

### Foto de jugador PL
URL: `https://resources.premierleague.com/premierleague/photos/players/250x250/p{playerId}.png`
Ejemplo Raya: `https://resources.premierleague.com/premierleague/photos/players/250x250/p360351.png`

### Mapa nombre → PL team ID
```javascript
EPL_TEAM_ID_MAP = {
  'Arsenal':1, 'Aston Villa':2, 'Bournemouth':127, 'Brentford':130,
  'Brighton & Hove Albion':131, 'Burnley':43, 'Chelsea':4, 'Crystal Palace':6,
  'Everton':7, 'Fulham':34, 'Leeds United':9, 'Liverpool':10,
  'Manchester City':11, 'Manchester United':12, 'Newcastle United':23,
  'Nottingham Forest':15, 'Sunderland':29, 'Tottenham Hotspur':21,
  'West Ham United':25, 'Wolverhampton Wanderers':38,
}
```

### Regenerar datos (si se necesita actualizar)
```bash
cd "/Users/rodrigo/Documents/Claude/Projects/TFM Universidad Europea/barca-dashboard"
source venv/bin/activate
python scripts/03_fetch_epl_detail.py  # requiere internet, ~60 llamadas API PL
```

---

## 10. MAPA DE IDs API-SPORTS.IO — ESCUDOS

### La Liga (20 equipos)
| Equipo | ID | Estado |
|--------|-----|--------|
| FC Barcelona | 529 | ✅ |
| Real Madrid | 541 | ✅ |
| Villarreal CF | 533 | ✅ |
| Atlético de Madrid | 530 | ✅ |
| Real Betis | 543 | ✅ |
| Celta | 538 | ✅ |
| Getafe CF | 546 | ✅ |
| Rayo Vallecano | 728 | ✅ |
| Valencia CF | 532 | ✅ |
| Real Sociedad | 548 | ✅ |
| RCD Espanyol | 540 | ✅ |
| Athletic Club | 531 | ✅ |
| Elche CF | `/static/img/elche.svg` | ✅ SVG local |
| Deportivo Alavés | `/static/img/alaves.svg` | ✅ SVG local |
| Sevilla FC | 536 | ✅ |
| CA Osasuna | 727 | ✅ |
| RCD Mallorca | 798 | ✅ |
| Levante UD | `/static/img/levante.svg` | ✅ SVG oficial |
| Girona FC | 547 | ✅ |
| Real Oviedo | `/static/img/oviedo.svg` | ✅ SVG local |

### Premier League — en `EPL_MAP`
Arsenal=42, Man City=50, Man Utd=33, Aston Villa=66, Liverpool=40, Bournemouth=35, Sunderland=56, Brighton=51, Brentford=55, Chelsea=49, Fulham=36, Newcastle=34, Everton=45, Leeds=63, Crystal Palace=52, Nottm Forest=65, Spurs=47, West Ham=48, Burnley=44, Wolves=39

### Bundesliga — en `BUNDESLIGA_MAP`
Bayern=157, Dortmund=165, RB Leipzig=173, Stuttgart=172, Hoffenheim=167, Leverkusen=168, Freiburg=160, Frankfurt=169, Augsburg=170, Mainz=164, Union Berlin=176, Mönchengladbach=163, HSV=180, Köln=192, Werder=162, Wolfsburg=161, Heidenheim=2835, St.Pauli=185

### Serie A — en `SERIEA_MAP`
Inter=505, Napoli=492, Roma=497, Como=512, Milan=489, Juventus=496, Atalanta=499, Bologna=500, Lazio=487, Udinese=494, Sassuolo=488, Parma=491, Torino=503, Cagliari=490, Fiorentina=502, Genoa=495, Lecce=507, Cremonese=511, Verona=504, Pisa=517

### Ligue 1 — en `LIGUE1_MAP`
PSG=85, Lens=116, Lille=79, Lyon=80, Marseille=81, Rennes=111, Monaco=91, Strasbourg=95, Lorient=1082, Toulouse=96, Paris FC=109, Brest=526, Angers=78, Le Havre=1041, Auxerre=77, Nice=103, Nantes=83, Metz=112

---

## 11. DATOS CLAVE VERIFICADOS

### La Liga 2025/26 (38 JJ completas)
| Métrica | Valor |
|---------|-------|
| Campeón | FC Barcelona (94 pts) |
| Máx. goles equipo | FC Barcelona (95 GF) |
| Mayor xG equipo | FC Barcelona (99.67) |
| Menor xGA equipo | Real Madrid (44.99) |
| Máx. goleador | Kylian Mbappé (Real Madrid, 25g) |
| Máx. asistente | Lamine Yamal (Barcelona, 11a) |
| Más G+A | Kylian Mbappé (30 G+A) |
| Más minutos | Ionuț Radu (Celta, 3420 min) |

### Premier League 2025/26 (38 JJ)
| Campeón | Arsenal (85 pts) |
|---------|-----------------|
| Máx. goleador | Erling Haaland (Man City, 27g) |
| Máx. asistente | Bruno Fernandes (Man Utd, 21a) |
| Más G+A | Erling Haaland (35 G+A) |
| Más minutos | Virgil van Dijk (Liverpool, 3420 min) |

### Bundesliga 2025/26 (34 JJ)
| Campeón | Bayern München (89 pts) |
|---------|----------------------|
| Máx. goleador | Harry Kane (Bayern, 36g) |
| Máx. asistente | Michael Olise (Bayern, 19a) |
| Más minutos | Noah Atubolu (SC Freiburg, 3060 min) |

### Serie A 2025/26 (38 JJ)
| Campeón | FC Internazionale (87 pts) |
|---------|--------------------------|
| Máx. goleador | Lautaro Martínez (Inter, 17g) |
| Máx. asistente | Federico Dimarco (Inter, 16a) |
| Más minutos | Wladimiro Falcone (US Lecce, 3420 min) |

### Ligue 1 2025/26 (34 JJ)
| Campeón | Paris Saint-Germain (76 pts) |
|---------|------------------------------|
| Máx. goleador | Esteban Lepaul (Angers/Rennes, 21g) |
| Máx. asistente | Ludovic Ajorque (Brest, 9a) |
| Más minutos | Jordan Lefort (Angers, 3060 min) |

---

## 12. ÚLTIMAS ACCIONES REALIZADAS (esta sesión)

1. Implementación completa de las 5 ligas europeas con pipeline Understat idéntico al de La Liga
2. Cada liga tiene: splits JSON (total/home/away con xG/xGA/xPTS), players JSON, progression JSON
3. Ligue 1: títulos de sección cambiados a blanco por petición del usuario
4. EPL: sistema de detalle por equipo implementado (overlay lateral, 4 tabs: Estadio/Plantilla/Stats/Partidos)
5. EPL detail usa la API oficial de la Premier League (temporada 777 = 2025/26)
6. Script `03_fetch_epl_detail.py` creado y guardado (ejecutar en Mac del usuario)
7. Datos EPL detail ya cacheados en `epl_teams_detail.json` (306KB, 20 equipos)
8. Corregidos bugs de xPTS (comparación numérica con `Number()`)
9. Gráficos de progresión con leyenda blanca (`fontColor: '#e6edf3'` en generateLabels)
10. Fotos de jugadores guardadas para todas las ligas

---

## 13. PRÓXIMOS PASOS (ordenados por prioridad)

### Inmediatos — EPL Team Detail
1. **Cambiar panel lateral por panel/página independiente** (el usuario quiere vista nueva, no slide)
2. **Reformatear "Estadio":** 3 cards superiores: VICTORIAS/26, EMPATES/7, DERROTAS/5 (label arriba, número abajo). Ídem 3 cards inferiores (GOLES MARCADOS/71, etc.)
3. **Reformatear "Estadísticas":** Sin emojis, métrica en MAYÚSCULAS arriba, número abajo — igual que Resumen Temporada
4. **"JUGADORES PRIMER EQUIPO: 27"** en tab Plantilla
5. **Fotos de jugadores en Plantilla** no se muestran — verificar URL `resources.premierleague.com/...` o buscar alternativa CDN

### Medio plazo
6. Extender el sistema de detalle por equipo a La Liga (usando otra fuente, ya que LaLiga no tiene API pública equivalente)
7. Sección "Comparativa Europa" mejorada con scatter xG vs xGA para todos los equipos
8. Liga Portugal: buscar fuente de datos y completar la sección
9. Mejorar secciones de UCL/UEL con más detalle (estadísticas por equipo)

### Largo plazo — TFM
10. Sección Fair Play Financiero con datos de transferencias + valoraciones
11. Exportar vistas a PDF para la memoria escrita
12. Integrar análisis del dashboard con el texto del TFM (`TFM_25-26 2.pdf`)

---

## 14. CONVENCIONES QUE NO CAMBIAN

- **Puerto:** siempre 8080 (el 5000 está ocupado por AirPlay en Mac)
- **Temporada objetivo:** 2025/26 siempre
- **JSONs de `data/processed/` nunca se borran si hay error** — siempre se fusiona/preserva
- **Understat:** siempre usar los CSVs adjuntos, no scraping (que puede fallar)
- **Chart.js:** siempre `chart.destroy()` antes de crear nueva instancia
- **Nombres de equipos:** siempre nombres oficiales de cada liga (no abreviaciones)
- **Dark mode:** `#0d1117` fondo, `#161b22` cards — nunca fondo blanco en el dashboard
- **Tipografía:** Arial/Helvetica, sin Google Fonts
- **xPTS coloreado:** verde = equipo superó expectativas (Pts > xPTS), rojo = no las alcanzó (Pts < xPTS)

# CONTEXTO TFM — FC Barcelona Analytics Dashboard
> Documento de estado para continuación del proyecto. Generado: junio 2026.

---

## 1. IDENTIFICACIÓN DEL PROYECTO

**Título TFM:** Análisis de Big Data Deportivo — FC Barcelona Analytics Department  
**Institución:** Universidad Europea  
**Entorno:** MacBook Air del usuario  
**Ruta del proyecto:** `/Users/rodrigo/Documents/Claude/Projects/TFM Universidad Europea/barca-dashboard/`  
**Puerto local:** http://localhost:8080  
**Email usuario:** rm386196@gmail.com

---

## 2. OBJETIVO

Construir una **web local personalizada** (Flask + HTML/JS) para el análisis de estadísticas del FC Barcelona y las principales ligas europeas. El dashboard sirve como herramienta analítica para el TFM y debe cubrir:

- Estadísticas completas de La Liga 2025/26 (clasificación, xG, xGA, xPTS, jugadores)
- Champions League y Europa League (clasificaciones generales)
- Top 5 ligas europeas + Ligue 1 + Liga Portugal (tablas comparativas)
- Análisis detallado del FC Barcelona (partidos, jugadores, mercado, copas)
- Interfaz visual profesional con identidad de marca de cada competición

---

## 3. ARQUITECTURA TÉCNICA

### Stack
- **Backend:** Python 3 + Flask (servidor local, puerto 8080)
- **Frontend:** HTML5 + Vanilla JS + Chart.js 4.4.0
- **Datos:** JSON estáticos servidos por Flask (generados desde CSVs)
- **Sin base de datos** — todo en ficheros JSON en `data/processed/`

### Comandos para arrancar
```bash
cd "/Users/rodrigo/Documents/Claude/Projects/TFM Universidad Europea/barca-dashboard"
source venv/bin/activate
python app.py
# Abrir: http://localhost:8080
```

### Regenerar datos (si se actualizan CSVs)
```bash
python scripts/01_process_data.py   # procesa Kaggle CSVs → JSONs
python scripts/02_fetch_understat.py  # scraping Understat (requiere internet)
```
> ⚠️ El script de Understat tiene protección anti-borrado: si falla la conexión, NO sobreescribe los datos existentes.

---

## 4. ESTRUCTURA DE ARCHIVOS

```
barca-dashboard/
├── app.py                          ← Servidor Flask (todas las rutas API)
├── templates/
│   └── index.html                  ← Dashboard completo (SPA, ~1600 líneas)
├── static/
│   └── img/
│       ├── campnou.jpg             ← Fondo portada (usuario debe guardar)
│       ├── barca-logo.png          ← Escudo Barça (usuario debe guardar)
│       ├── laliga.png              ← Logo LaLiga viejo (fallback)
│       ├── laligaea.png            ← Logo LaLiga EA Sports nuevo ✅ GUARDADO
│       ├── bundesliga.svg          ← Logo Bundesliga ✅
│       ├── ucl.png                 ← Logo UCL ✅ GUARDADO
│       ├── uel.png                 ← Logo UEL ✅ GUARDADO
│       ├── premier.png             ← Logo Premier ✅ GUARDADO
│       ├── seriea.png              ← Logo Serie A ✅ GUARDADO
│       ├── ligue1.png              ← Logo Ligue 1 ✅ GUARDADO
│       ├── ligaportugal.png        ← Logo Liga Portugal ✅ GUARDADO
│       ├── laliga_mbappe.png       ← Foto Mbappé (Top Rendimiento) ✅
│       ├── laliga_yamal.png        ← Foto Lamine Yamal ✅
│       └── laliga_radu.png         ← Foto Ionuț Radu (Celta) ✅
├── data/
│   ├── raw/                        ← CSVs originales (no modificar)
│   │   ├── games.csv               ← Kaggle Transfermarkt (todos los partidos)
│   │   ├── player_valuations.csv   ← Kaggle Transfermarkt (valoraciones)
│   │   ├── players_data-2025_2026.csv  ← Kaggle FBref (stats jugadores)
│   │   ├── transfers.csv           ← Kaggle Transfermarkt (transferencias)
│   │   ├── laliga_understat_table.csv  ← Understat La Liga total (38 PJ)
│   │   ├── laliga_understat_home.csv   ← Understat La Liga local (19 PJ)
│   │   └── laliga_understat_away.csv   ← Understat La Liga visitante (19 PJ)
│   │   └── laliga_understat_players.csv ← Understat jugadores La Liga
│   └── processed/                  ← JSONs generados (sirven al frontend)
│       ├── league_tables.json      ← Clasificaciones 5 ligas + xG/xGA
│       ├── laliga_splits.json      ← La Liga: total + local + visitante (con xPTS)
│       ├── laliga_players_understat.json  ← 600 jugadores La Liga con xG/xA
│       ├── laliga_progression.json ← Puntos acumulados por jornada (34 JJ)
│       ├── ucl_table.json          ← UCL 2025/26 (36 equipos)
│       ├── uel_table.json          ← UEL 2025/26 (36 equipos)
│       ├── barca_games.json        ← Todos los partidos del Barça
│       ├── barca_cl_games.json     ← Partidos Barça en UCL
│       ├── barca_cdr_games.json    ← Partidos Barça en Copa del Rey
│       ├── barca_suc_games.json    ← Partidos Barça en Supercopa
│       ├── barca_players.json      ← Estadísticas jugadores Barça (FBref)
│       ├── barca_players_advanced.json  ← Stats avanzadas jugadores Barça
│       ├── barca_transfers.json    ← Transferencias del Barça
│       ├── barca_valuations.json   ← Valoraciones de mercado plantilla
│       └── barca_squad_value_history.json  ← Evolución valor plantilla
└── scripts/
    ├── 01_process_data.py          ← Procesa todos los Kaggle CSVs
    └── 02_fetch_understat.py       ← Scraping Understat (con protección anti-borrado)
```

---

## 5. FUENTES DE DATOS

| Fuente | Datos | Estado |
|--------|-------|--------|
| Kaggle Transfermarkt (`games.csv`) | Resultados de partidos, todas las ligas y competiciones | ✅ Descargado y procesado |
| Kaggle Transfermarkt (`player_valuations.csv`) | Historial valoraciones de mercado | ✅ |
| Kaggle Transfermarkt (`transfers.csv`) | Transferencias históricas | ✅ |
| Kaggle FBref (`players_data-2025_2026.csv`) | Stats 2025/26 de jugadores top 5 ligas | ✅ |
| Understat (`laliga_understat_*.csv`) | xG, xGA, xPTS, PPDA — La Liga 38 PJ total/local/visit. | ✅ Adjuntados manualmente por el usuario |
| Understat scraping | xG por partido del Barça, tablas con xG otras ligas | ⚠️ Script disponible pero scraping bloqueado en sandbox |

### Limitación conocida
- `games.csv` de Kaggle solo tiene **34 jornadas** de La Liga 2025/26 (temporada incompleta en el dataset). La clasificación total usa los CSVs de Understat (38 PJ completas).
- El script de Understat funciona desde la Mac del usuario (con internet), pero puede ser bloqueado si Understat detecta scraping.
- Si el scraping de Understat falla, **los datos de Kaggle se preservan** (no se sobreescriben).

---

## 6. RUTAS API (app.py)

```
GET /                              → index.html (SPA)
GET /api/barca/games               → Todos los partidos del Barça
GET /api/barca/matches/understat   → Partidos Barça con xG (Understat)
GET /api/barca/champions           → Partidos Barça en UCL
GET /api/barca/copadelrey          → Partidos Barça en Copa del Rey
GET /api/barca/supercopa           → Partidos Barça en Supercopa
GET /api/barca/players             → Jugadores Barça (FBref stats)
GET /api/barca/players/understat   → Jugadores Barça (Understat xG/xA)
GET /api/barca/players/advanced    → Stats avanzadas jugadores Barça
GET /api/barca/transfers           → Transferencias del Barça
GET /api/barca/valuations          → Valoraciones de mercado plantilla
GET /api/barca/squad-value-history → Evolución valor total plantilla
GET /api/laliga/players            → 600 jugadores La Liga (Understat)
GET /api/laliga/splits             → Clasificación La Liga (total/local/visitante)
GET /api/laliga/progression        → Puntos acumulados por jornada
GET /api/ucl/table                 → Clasificación UCL (36 equipos)
GET /api/uel/table                 → Clasificación UEL (36 equipos)
GET /api/leagues/tables            → Clasificaciones 5 ligas (con xG si disponible)
GET /api/leagues/players           → Todos los jugadores top 5 ligas (FBref)
GET /api/status                    → Estado de todos los archivos de datos
```

---

## 7. SECCIONES DEL DASHBOARD — ESTADO

### PORTADA (Hero)
- **Estado:** ✅ Funcional con pendientes menores
- Fondo: imagen `campnou.jpg` del Camp Nou con overlay oscuro
- Escudo Barça flotante (sin animación, sin halo dorado)
- Título: "FC Barcelona – Analytics Department" en Arial/Helvetica mayúsculas
- 8 tarjetas de ligas en grid 4+4 con fondo blanco (logos sobre blanco)
- Botón "Entrar al Dashboard del Barça"
- **⚠️ PENDIENTE:** El logo de LaLiga EA Sports en las tarjetas muestra el logo viejo. El usuario adjuntó un nuevo logo (solo texto "LALIGA" en rojo sobre negro) que debe guardarse como `static/img/laligaea.png` (sobreescribiendo el actual)

### PÁGINAS DE LIGAS (al clicar tarjeta)
Cada liga abre su página dedicada con:
- Hero con logo oficial + fondo de color de la liga
- 4 KPI boxes (Campeón/Líder, Goleador, Mayor xG, Menor xGA)
- Tabla de clasificación con escudos
- Top Rendimiento (goleador, asistente, G+A, mayor xG)
- Gráfico específico

#### LA LIGA EA SPORTS — Estado: ✅ Funcional (con pendientes)
- Datos: Understat 2025/26, 38 jornadas completas
- Hero: fondo blanco, logo en caja negra + "Temporada 2025/26 · España"
- Color oficial: `#EE3524` (Pantone Red 032C)
- KPIs: Campeón (Barça 94pts), Goleador (Barça 95GF), Mayor xG (Barça 99.67), Menor xGA (Real Madrid 44.99)
- Tabla: nombres oficiales LaLiga + escudos via `media.api-sports.io`
- Columnas: #, Equipo, PJ, G, E, P, GF, GC, DG, Pts, xG, xGA, **xPTS** (no xG-xGA)
- Filtro: Partidos totales / Local / Visitante (con datos Understat reales)
- Top Rendimiento: Mbappé (25G), Lamine Yamal (11A), fotos en círculo sin iniciales
- Gráfico: **línea de progresión de puntos por jornada** (20 equipos, 34 JJ disponibles)
- **⚠️ PENDIENTE:** 
  - Logo en hero: el adjuntado (solo "LALIGA" texto rojo sobre negro) debe reemplazar `laligaea.png`
  - Escudos incorrectos: Elche CF, Deportivo Alavés, Levante UD, Real Oviedo (IDs de API-Football equivocados)
  - Gráfico de progresión: solo 34 jornadas (Kaggle), faltan 4 para completar las 38

#### PREMIER LEAGUE — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (35 PJ)
- Sin xG/xGA (Understat no scrapeó exitosamente)
- Top performers: FBref CSV `players_data-2025_2026.csv`

#### BUNDESLIGA — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (32 PJ)
- Logo: `bundesliga.svg` local

#### SERIE A — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (35 PJ)

#### LIGUE 1 — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (31 PJ)

#### LIGA PORTUGAL — Estado: ⚠️ Datos limitados
- No está en FBref CSV ni en Understat scraping
- Muestra datos parciales de jugadores portugueses si los hay en el CSV

#### UEFA CHAMPIONS LEAGUE — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (36 equipos)
- Tabla general de todos los equipos (no solo el Barça)
- KPIs, buscador, zonas de color por clasificación
- Top Rendimiento: equipos más goleadores y mejor defensa

#### UEFA EUROPA LEAGUE — Estado: ✅ Funcional
- Datos: Kaggle games.csv 2025/26 (36 equipos)
- Mismo formato que UCL

### DASHBOARD FC BARCELONA (secciones internas)

#### Equipo — Estado: ✅ Funcional
- KPIs: Puntos LaLiga, Diferencia de goles, xG total, xGA total
- Gráfico xG vs xGA por partido (Understat, si disponible)
- Gráfico evolución de puntos acumulados
- Forma reciente (últimos 10 partidos, píldoras W/D/L)

#### Partidos — Estado: ✅ Funcional
- Tabla filtrable por rival, resultado, competición
- Usa datos Understat si disponibles, sino Kaggle

#### Jugadores — Estado: ✅ Funcional
- Tabla de 29 jugadores del Barça con stats FBref
- Filtro por posición y búsqueda
- Tabla adicional con xG/xA de Understat (si disponible)

#### Champions League — Estado: ✅ Funcional
- KPIs, forma reciente, tabla de resultados del Barça en UCL

#### Copa & Supercopa — Estado: ✅ Funcional
- Copa del Rey (15 partidos) y Supercopa (4 partidos) del Barça

#### Stats Avanzadas — Estado: ✅ Funcional
- 4 vistas: Disparo, Defensa & Duelos, Tiempo de juego, Porteros
- Gráficos: Goles vs xG y minutos por jugador

#### Plantilla & Mercado — Estado: ✅ Funcional
- Gráfico evolución valor total plantilla (histórico)
- Resumen de transferencias (inversión vs ingresos)
- Tabla de movimientos filtrable por dirección (IN/OUT) y temporada

#### Comparativa Europa — Estado: ✅ Funcional
- Tabs por liga (LaLiga, Premier, Bundesliga, Serie A, Ligue 1)
- Gráfico scatter xG vs xGA todos los equipos

---

## 8. DECISIONES DE DISEÑO

### Colores
- **Fondo general:** `#0d1117` (dark mode)
- **Cards:** `#161b22`
- **Barça azul:** `#004D98`
- **Barça rojo:** `#A50044`
- **Barça dorado:** `#EDBB00`
- **LaLiga rojo oficial:** `#EE3524` (Pantone Red 032C)
- **Éxito/verde:** `#3fb950`
- **Peligro/rojo:** `#f85149`
- **Advertencia/amarillo:** `#d29922`

### Tipografía
- **Todo el dashboard:** Arial, Helvetica Neue, Helvetica, sans-serif
- **Portada título:** Arial 700, uppercase, letter-spacing 0.12em

### Logos de ligas en portada
- Fondo de tarjeta: **blanco** (`#ffffff`)
- Si la imagen falla: badge CSS de color con siglas
- Solo imagen oficial, sin texto ni banderas en las tarjetas

### Escudos en tabla La Liga
- CDN: `https://media.api-sports.io/football/teams/{ID}.png`
- Sin letras de fallback — si no carga, imagen transparente (limpio)
- Tamaño: 24px en tabla, 40px en KPI boxes

### Hero del dashboard interno (Barça)
- Logo Barça: estático (sin animación), sin filtro dorado
- Texto: "FC Barcelona – Analytics Department"

### Páginas de liga
- Cada liga tiene su color de hero:
  - La Liga: fondo blanco con borde rojo `#EE3524`
  - UCL: `linear-gradient(135deg, #001a5e, #0a3d8f)`
  - Premier: `linear-gradient(135deg, #3d195b, #5c2d8b)`
  - Bundesliga: `linear-gradient(135deg, #d20515, #a00010)`
  - Serie A: `linear-gradient(135deg, #024494, #001f6b)`
  - Ligue 1: `linear-gradient(135deg, #091c3e, #1a3a6e)`
  - Liga Portugal: `linear-gradient(135deg, #006600, #004400)`
  - UEL: `linear-gradient(135deg, #f05000, #b03000)`

---

## 9. MAPA DE NOMBRES DE EQUIPOS

Los equipos de La Liga tienen 3 variantes de nombre que hay que mantener consistentes:

| Nombre Kaggle (Transfermarkt) | Nombre Understat | Nombre oficial LaLiga |
|-------------------------------|-----------------|----------------------|
| Futbol Club Barcelona | Barcelona | FC Barcelona |
| Real Madrid Club de Fútbol | Real Madrid | Real Madrid |
| Villarreal Club de Fútbol S.A.D. | Villarreal | Villarreal CF |
| Club Atlético de Madrid S.A.D. | Atletico Madrid | Atlético de Madrid |
| Real Betis Balompié S.A.D. | Real Betis | Real Betis |
| Real Club Celta de Vigo S. A. D. | Celta Vigo | Celta |
| Getafe Club de Fútbol S. A. D. Team Dubai | Getafe | Getafe CF |
| Athletic Club Bilbao | Athletic Club | Athletic Club |
| Real Sociedad de Fútbol S.A.D. | Real Sociedad | Real Sociedad |
| Club Atlético Osasuna | Osasuna | CA Osasuna |
| Rayo Vallecano de Madrid S. A. D. | Rayo Vallecano | Rayo Vallecano |
| Valencia Club de Fútbol S. A. D. | Valencia | Valencia CF |
| Reial Club Deportiu Espanyol de Barcelona S.A.D. | Espanyol | RCD Espanyol de Barcelona |
| Elche Club de Fútbol S.A.D. | Elche | Elche CF |
| Real Club Deportivo Mallorca S.A.D. | Mallorca | RCD Mallorca |
| Girona Fútbol Club S. A. D. | Girona | Girona FC |
| Sevilla Fútbol Club S.A.D. | Sevilla | Sevilla FC |
| Deportivo Alavés S. A. D. | Alaves | Deportivo Alavés |
| Levante Unión Deportiva S.A.D. | Levante | Levante UD |
| Real Oviedo S.A.D. | Real Oviedo | Real Oviedo |

El `LALIGA_MAP` en `index.html` usa los **nombres oficiales LaLiga** como clave y el `LALIGA_SHORT` mapea Understat → oficial. El `LALIGA_NAMES` en los scripts Python mapea Understat → oficial.

---

## 10. IDs DE API-FOOTBALL PARA ESCUDOS (media.api-sports.io)

Los correctos y los pendientes de corregir:

| Equipo | ID actual | Estado |
|--------|-----------|--------|
| FC Barcelona | 529 | ✅ Correcto |
| Real Madrid | 541 | ✅ Correcto |
| Villarreal CF | 533 | ✅ Correcto |
| Atlético de Madrid | 530 | ✅ Correcto |
| Real Betis | 543 | ✅ Correcto |
| Celta | 538 | ✅ Correcto |
| Getafe CF | 546 | ✅ Correcto |
| Rayo Vallecano | 728 | ✅ Correcto |
| Valencia CF | 532 | ✅ Correcto |
| Real Sociedad | 548 | ✅ Correcto |
| RCD Espanyol de Barcelona | 540 | ✅ Correcto |
| Athletic Club | 531 | ✅ Correcto |
| Elche CF | 547 | ⚠️ **PENDIENTE — ID incorrecto** |
| Deportivo Alavés | 720 | ⚠️ **PENDIENTE — verificar** |
| Sevilla FC | 536 | ✅ Correcto |
| CA Osasuna | 727 | ✅ Correcto |
| RCD Mallorca | 798 | ✅ Correcto |
| Levante UD | 544 | ⚠️ **PENDIENTE — verificar** |
| Girona FC | 547 | ⚠️ **PENDIENTE — ID incorrecto (mismo que Elche)** |
| Real Oviedo | 724 | ⚠️ **PENDIENTE — verificar** |

IDs correctos para actualizar (verificar en https://www.api-football.com/):
- Elche CF: ~880
- Deportivo Alavés: ~720 (puede estar bien)
- Levante UD: ~724
- Girona FC: ~547 (conflicto con Elche — uno está mal)
- Real Oviedo: ~798 (conflicto con Mallorca)

---

## 11. ÚLTIMAS ACCIONES REALIZADAS

1. Procesados 3 CSVs de Understat (total + local + visitante) en un único `laliga_splits.json` con xPTS
2. Columna xG-xGA reemplazada por **xPTS** en la tabla de La Liga
3. Gráfico de barras (GF vs GC) reemplazado por **gráfico de progresión de puntos** por jornada (línea animada, 20 equipos, colores distintos)
4. Ruta API nueva: `/api/laliga/progression`
5. Escudos cambiados a `media.api-sports.io` (más fiables que Wikipedia SVG)
6. `teamLogo()` actualizado: sin texto de fallback, imagen transparente si falla
7. Hero La Liga: contenedor negro para el logo (permite ver el rojo del logo sobre cualquier fondo)
8. `renderLeagueChart()` completamente reescrita como línea de progresión con Chart.js
9. Protección anti-borrado en `02_fetch_understat.py` (no sobreescribe si falla)
10. `renderLeagueTop()` para La Liga usa `/api/laliga/players` (Understat, 600 jugadores)

---

## 12. PRÓXIMOS PASOS PENDIENTES

### Inmediatos (sesión siguiente)
1. **Corregir logo LaLiga:** el usuario adjuntó el logo definitivo (texto "LALIGA" rojo sobre negro). Debe guardarse sobreescribiendo `static/img/laligaea.png`
2. **Corregir IDs de escudos incorrectos:** Elche CF, Deportivo Alavés, Levante UD, Girona FC, Real Oviedo
3. **Añadir texto "Temporada 2025/26 · España"** debajo del logo en el hero de La Liga (ya está en el HTML pero verificar que se vea)

### Medio plazo (siguientes secciones)
4. **Completar páginas de otras ligas** con el mismo nivel de detalle que La Liga:
   - Premier League: adjuntar CSV de Understat o FBref para xG/xPTS
   - Bundesliga: mismo
   - Serie A: mismo
   - Ligue 1: mismo
5. **Liga Portugal:** buscar y adjuntar CSV de datos para completar la sección
6. **Gráfico de progresión 38 JJ completas:** las 4 jornadas finales faltan en Kaggle; el usuario puede adjuntar los resultados manualmente
7. **Sección UCL — detalle por equipo:** actualmente solo hay tabla general; añadir detalles de cada equipo
8. **Top performers con fotos para otras ligas:** igual que La Liga (el usuario adjunta las fotos)
9. **Sección de comparativa avanzada:** scatter xG vs xGA con todos los equipos europeos

### Largo plazo / TFM
10. **Memoria escrita del TFM:** ya tiene partes escritas (`TFM_25-26 2.pdf`); integrar los análisis del dashboard con el texto
11. **Exportar vistas a PDF:** para incluir capturas en la memoria
12. **Sección de Fair Play Financiero:** usar datos de transferencias + valoraciones para análisis de sostenibilidad económica del Barça

---

## 13. COSAS QUE NO CAMBIAN (convenciones acordadas)

- **Puerto:** siempre 8080 (el 5000 está ocupado por AirPlay en Mac)
- **No usar `localStorage`** en el frontend
- **Temporada objetivo:** 2025/26 (season='2025' en Kaggle, '2025' en Understat)
- **Temporada Understat:** probar primero '2025', fallback a '2024'
- **Los JSONs de `data/processed/` nunca se borran si hay error** — siempre se fusiona/preserva
- **Formato de datos La Liga:** usar siempre los CSVs adjuntos de Understat (no los generados de Kaggle) para los datos finales de clasificación
- **Nombres oficiales:** siempre los de la plataforma LaLiga (columna "Nombre oficial LaLiga" de la tabla de arriba)
- **Emojis:** eliminados de los títulos de Top Rendimiento
- **Iniciales en círculos de jugadores:** eliminadas — solo imagen o círculo oscuro vacío
- **Chart.js:** siempre destruir instancia anterior (`chart.destroy()`) antes de crear nueva

---

## 14. DATOS CLAVE VERIFICADOS (La Liga 2025/26, 38 JJ)

| Métrica | Valor |
|---------|-------|
| Campeón | FC Barcelona (94 pts) |
| Máx. goles marcados | FC Barcelona (95 GF) |
| Mayor xG | FC Barcelona (99.67) |
| Menor xGA | Real Madrid (44.99) |
| Máx. goleador individual | Kylian Mbappé (Real Madrid, 25 goles, 25.8 xG) |
| Máx. asistente | Lamine Yamal (FC Barcelona, 11 asistencias) |
| Máx. G+A | Kylian Mbappé (30 G+A) |
| Más minutos | Ionuț Radu (Celta, 3420 min — portero) |

| Fotos jugadores guardadas | Archivo | Asignación |
|--------------------------|---------|------------|
| Kylian Mbappé (Real Madrid, blanco) | `laliga_mbappe.png` | Máx. Goleador + Más G+A |
| Lamine Yamal (Barça, azulgrana) | `laliga_yamal.png` | Máx. Asistente |
| Ionuț Radu (Celta, rosa Estrella Galicia) | `laliga_radu.png` | Más minutos |

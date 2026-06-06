# FC Barcelona – Dashboard Analítico (TFM)

Dashboard web local para análisis de datos del FC Barcelona.

## Requisitos

- Python 3.9 o superior (viene con macOS, verifica con `python3 --version`)

## Instalación (solo la primera vez)

```bash
# 1. Ir a la carpeta del proyecto
cd "ruta/a/TFM Universidad Europea/barca-dashboard"

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar el entorno
source venv/bin/activate

# 4. Instalar dependencias
pip install flask pandas requests beautifulsoup4
```

## Uso

Cada vez que quieras usar el dashboard:

```bash
# Activar entorno (si no está activo)
source venv/bin/activate

# Paso 1: Procesar los datos de Kaggle (solo hace falta una vez, o al actualizar CSVs)
python scripts/01_process_data.py

# Paso 2: Descargar datos de Understat (requiere internet, tarda ~2 minutos)
python scripts/02_fetch_understat.py

# Paso 3: Lanzar el servidor
python app.py
```

Luego abre el navegador en: **http://localhost:5000**

## Estructura

```
barca-dashboard/
├── data/
│   ├── raw/           ← CSVs originales de Kaggle
│   └── processed/     ← JSONs generados por los scripts
├── scripts/
│   ├── 01_process_data.py    ← limpia CSVs → JSONs
│   └── 02_fetch_understat.py ← scraping Understat → JSONs
├── templates/
│   └── index.html     ← interfaz web completa
├── app.py             ← servidor Flask (API + web)
└── README.md
```

## Secciones del dashboard

- **Equipo**: KPIs, xG/xGA por partido, evolución de puntos, forma reciente
- **Partidos**: tabla de resultados filtrable con competición y resultado
- **Jugadores**: estadísticas de los 29 jugadores del Barça, xG por jugador (Understat)
- **Plantilla & Mercado**: valor histórico de plantilla, transferencias con fee y valor de mercado
- **Comparativa Europa**: tablas de LaLiga, Premier, Bundesliga, Serie A y Ligue 1 con xG/xGA

## Fuentes de datos

- [Kaggle – Player Scores (Transfermarkt)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- [Kaggle – Football Players Stats 2025/26](https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026)
- [Understat](https://understat.com) – xG, xGA, NPxG, xPTS

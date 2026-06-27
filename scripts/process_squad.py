import pandas as pd

df = pd.read_parquet('data/raw/all_players_data.parquet')


df = df[df['current_club_name'] == 'FC Barcelona']

features = [
    "name",
    "posicion", 
    "90s", 
    "pct_pass_accuracy", 
    "key_passes_per_90", 
    "goals_per_90", 
    "assists_per_90", 
    "interceptions_per_90", 
    "recoveries_per_90", 
    "tackles_won_per_90", 
    "final_third_touches_per_90", 
    "Yellow Cards", 
    "Straight Red Cards"
]

df['name'] = df['name'].str.join(' ')
df['name'] = df['name'].str.title()


df = df[features]

df = df.fillna(0)


df.to_json("data/processed/andvanced_stats.json", orient = 'records')

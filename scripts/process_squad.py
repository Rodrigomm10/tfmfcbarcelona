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

df['current_club_name']


club_stats = {
    "team_name": "FC Barcelona",
    "total_market_value_eur": df['market_value_in_eur'].sum(),
    "players_used": int(df[df['90s'] > 0]['player_id'].nunique()), # Cuántos jugadores tuvieron minutos
    "total_90s_played": df['90s'].sum(),
    "total_goals": int(df['Goals'].sum()),
    "total_shots": int(df['Total Shots'].sum()),
    "shots_on_target": int(df['Shots On Target ( inc goals )'].sum()),
    "big_chances_created": int(df['Total Big Chances Created'].sum()),
    "big_chances_missed": int(df['Total Big Chances Missed'].sum()),
    "big_chances_scored": int(df['Total Big Chances Scored'].sum()),
    "total_assists": int(df['Goal Assists'].sum()),
    "total_passes": int(df['Total Passes'].sum()),
    "successful_passes": int(df['Total Successful Passes ( Excl Crosses & Corners ) '].sum()),
    "final_third_touches": int(df['Final Third Touches'].sum()),
    "progressive_carries": int(df['Progressive Carries'].sum()),
    "successful_dribbles": int(df['Successful Dribbles'].sum()),
    "total_recoveries": int(df['Recoveries'].sum()),
    "total_interceptions": int(df['Interceptions'].sum()),
    "tackles_won": int(df['Tackles Won'].sum()),
    "aerial_duels_won": int(df['Aerial Duels won'].sum()),
    "goals_conceded": int(df[df['posicion'] == 'Goalkeeper']['Goals Conceded'].sum()),
    "clean_sheets": int(df[df['posicion'] == 'Goalkeeper']['Clean Sheets'].sum())
}
if club_stats['total_passes'] > 0:
    club_stats['team_pass_accuracy'] = round((club_stats['successful_passes'] / club_stats['total_passes']) * 100, 2)
else:
    club_stats['team_pass_accuracy'] = 0.0
if club_stats['total_shots'] > 0:
    club_stats['team_conversion_rate'] = round((club_stats['total_goals'] / club_stats['total_shots']) * 100, 2)
else:
    club_stats['team_conversion_rate'] = 0.0
total_big_chances = club_stats['big_chances_scored'] + club_stats['big_chances_missed']
if total_big_chances > 0:
    club_stats['big_chances_conversion'] = round((club_stats['big_chances_scored'] / total_big_chances) * 100, 2)
else:
    club_stats['big_chances_conversion'] = 0.0



club_df = pd.DataFrame([club_stats])
club_df.to_json("data/processed/barca_club_analysis.json", orient="records")

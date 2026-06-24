import polars as pl
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.metrics import silhouette_score as silo_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.decomposition import PCA
import json

# Function to see the goodness of the K
## we will use 
### Helper Functions

def plot_player_radar(dfs_list, index, feature_cols):
    # Funcion para graficar el radar
    df = dfs_list[index]
    target_player = df.iloc[0]
    matches = df.iloc[1:]
    
    labels = feature_cols
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  
    
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    
    colors = ['#1d3557', '#e63946', '#2a9d8f', '#a8dadc', '#f4a261', '#457b9d']
    
    target_values = target_player[labels].values.flatten().tolist()
    target_values += target_values[:1]
    
    ax.plot(angles, target_values, color=colors[0], linewidth=3, linestyle='-', 
            label=f"TARGET: {target_player['nombre']} ({target_player['equipo']})")
    ax.fill(angles, target_values, color=colors[0], alpha=0.15)
    
    for i, (_, match) in enumerate(matches.iterrows()):
        match_values = match[labels].values.flatten().tolist()
        match_values += match_values[:1]
        
        color = colors[i + 1] 
        
        ax.plot(angles, match_values, color=color, linewidth=1.5, linestyle='--', alpha=0.8,
                label=f"Match {i+1}: {match['nombre']} ({match['equipo']}) | Dist: {match['Statistic_compatibility']:.2f}")
    
    ax.set_theta_offset(np.pi / 2)  
    ax.set_theta_direction(-1)       
    
    plt.xticks(angles[:-1], labels, color='grey', size=10)
    
    plt.title(f"Stylistic Comparison Matrix: {target_player['nombre']}", size=16, color='#1d3557', y=1.1, weight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=True, shadow=True)
    
    plt.tight_layout()
    plt.show()



def plot_player_radar_scaled(dfs_list, index, feature_cols, full_dataset):
    df = dfs_list[index]
    target_player = df.iloc[0]
    matches = df.iloc[1:]
    
    labels = feature_cols
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] # Close the polygon loop
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    colors = ['#1d3557', '#e63946', '#2a9d8f', '#b5e2fa', '#f4a261', '#6a4c93']
    
    mins = full_dataset[labels].min().astype(float)
    maxs = full_dataset[labels].max().astype(float)
    
    def normalize(row):
        row_vals = row[labels].astype(float)
        return (row_vals - mins) / (maxs - mins + 1e-5)

    target_norm = normalize(target_player).values.flatten().tolist()
    target_norm += target_norm[:1]
    
    ax.plot(angles, target_norm, color=colors[0], linewidth=3.5, linestyle='-', 
            label=f"TARGET: {target_player['nombre']} ({target_player['equipo']})")
    ax.fill(angles, target_norm, color=colors[0], alpha=0.18)
    
    for i, (_, match) in enumerate(matches.iterrows()):
        match_norm = normalize(match).values.flatten().tolist()
        match_norm += match_norm[:1]
        
        color = colors[i + 1] 
        ax.plot(angles, match_norm, color=color, linewidth=1.5, linestyle='--', alpha=0.8,
                label=f"Match {i+1}: {match['nombre']} ({match['equipo']}) | Dist: {match['Statistic_compatibility']:.2f}")
    
    reference_labels = []
    for col in labels:
        max_val = maxs[col]
        reference_labels.append(f"{col}\n(Max: {max_val:.2f})")
    
    ax.set_theta_offset(np.pi / 2) 
    ax.set_theta_direction(-1)     
    
    ax.set_ylim(0, 1)              
    ax.set_yticklabels([])         
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(reference_labels, color='#2b2d42', size=9, weight='bold')
    ax.tick_params(axis='x', pad=22)
    
    plt.title(f"Stylistic Comparison Matrix: {target_player['nombre']}", size=16, color='#1d3557', y=1.12, weight='bold')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=True, shadow=True, fontsize=10)
    
    plt.tight_layout()
    plt.show()


def kmeans_wss(k, X):
    km = KMeans(
        n_clusters=int(k),        
        n_init=25,                
        max_iter=75,             
        random_state=69,       
        algorithm="lloyd"         
    ).fit(X)
    return float(km.inertia_) 
def silhouette_for_k(k, X):
    km = KMeans(
        n_clusters=int(k),
        n_init=25,
        max_iter=75,
        random_state=69,
        algorithm="lloyd"
    ).fit(X)
    return float(silo_score(X, km.labels_, metric="euclidean"))

# Function to turn into Json file (trial)


def generate_cluster_specific_ui_json(position_configs, output_filename="scouting_master_database.json"):
    """
    Unifies all players into a single JSON file. Dynamically selects radar columns 
    based on the specific player's cluster ID.
    """
    master_database = []
    for config in position_configs:
        dfs_list = config["dfs_list"]
        full_dataset = config["full_dataset"]
        pos_label = config["pos_label"]
        cluster_profile_map = config["cluster_profile_map"] # Dictionary mapping cluster_id -> column_list
        for df in dfs_list:
            if df.empty:
                continue
            df_clean = df.fillna(0)
            target_row = df_clean.iloc[0]
            similar_rows = df_clean.iloc[1:]
            # 1. Determine which specific feature columns to use based on the target player's cluster
            cluster_id = int(target_row["cluster"])
            feature_cols = cluster_profile_map.get(cluster_id)
            # Fallback if a cluster is missing from our map
            if feature_cols is None:
                print(f"Warning: Cluster {cluster_id} not defined in profile map for position {pos_label}. Skipping.")
                continue
            # 2. Grab global bounds for scaling this specific metric list
            mins = full_dataset[feature_cols].min().fillna(0).astype(float)
            maxs = full_dataset[feature_cols].max().fillna(0).astype(float)
            def scale_stats(row):
                row_vals = row[feature_cols].astype(float)
                normalized = ((row_vals - mins) / (maxs - mins + 1e-5)) * 100
                return normalized.round().astype(int).tolist()
            # 3. Format Target Player profile
            player_entry = {
                "Player": str(target_row["nombre"]),
                "Pos": pos_label,
                "Cluster": cluster_id,
                "Team": str(target_row["equipo"]),
                "DisplayStats": {
                    "PJ": int(target_row.get("Matches Played", target_row.get("Partidos Jugados", 0))),
                    "G": int(target_row.get("Goals", target_row.get("raw_goals", 0))),
                    "A": int(target_row.get("Goal Assists", target_row.get("assists_per_90", 0) * (target_row.get("90s", 1)))),
                },
                "RadarLabels": list(feature_cols),
                "MainPlayerStats": scale_stats(target_row),
                "SimilarPlayers": []
            }
            # 4. Map the matching percentage
            max_dist = similar_rows["Statistic_compatibility"].max() if len(similar_rows) > 0 else 1.0
            if max_dist == 0: max_dist = 1.0
            # 5. Process the stylistic matches using the exact same columns
            for _, match_row in similar_rows.iterrows():
                dist = match_row["Statistic_compatibility"]
                pct = max(60, 100 - (dist / (max_dist + 1e-5) * 35))
                similar_entry = {
                    "Name": str(match_row["nombre"]),
                    "Team": str(match_row["equipo"]),
                    "MatchPercentage": f"{int(pct)}%",
                    "Stats": scale_stats(match_row)
                }
                player_entry["SimilarPlayers"].append(similar_entry)
            master_database.append(player_entry)
    # Save unified output
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(master_database, f, indent=2, ensure_ascii=False)
        
    print(f"Database unified perfectly! File saved to '{output_filename}' ({len(master_database)} profiles).")


#-------------------------------------------------------------------

df = pl.read_parquet('data/raw/new_data.parquet')

# posiciones
df.select(pl.col('posicion').unique())

df = df.with_columns((pl.col('Time Played') / 90.0).alias("90s"))

#----------------------------------------------------------------------

forwards = df.filter(( pl.col('posicion') == 'Forward' ) & (pl.col('Time Played') > 450.0))

forwards.filter(pl.col('equipo') == 'FC Barcelona').select('nombre') 

fw_features = forwards.with_columns([
    (pl.col("Shots On Target ( inc goals )").cast(pl.Float64) / pl.col("90s")).alias("shots_on_target_per_90"),
    (pl.col("Shots Off Target (inc woodwork)").cast(pl.Float64) / pl.col("90s")).alias("shots_off_target_per_90"),
    (pl.col("Total Shots").cast(pl.Float64) / pl.col("90s")).alias("total_shots_per_90"),
    (pl.col("Goals").cast(pl.Float64) / pl.col("90s")).alias("goals_per_90"),
    (pl.col("Goals Openplay").cast(pl.Float64) / pl.col("90s")).alias("goals_openplay_per_90"),
    (pl.col("Goals from Inside Box").cast(pl.Float64) / pl.col("90s")).alias("goals_inside_box_per_90"),
    (pl.col("Total Big Chances Scored").cast(pl.Float64) / pl.col("90s")).alias("big_chances_scored_per_90"),
    (pl.col("Total Big Chances Missed").cast(pl.Float64) / pl.col("90s")).alias("big_chances_missed_per_90"),
    (pl.col("Total Touches In Opposition Box").cast(pl.Float64) / pl.col("90s")).alias("box_touches_per_90"),
    (pl.col("Key Passes (Attempt Assists)").cast(pl.Float64) / pl.col("90s")).alias("key_passes_per_90"),
    (pl.col("Shots Created").cast(pl.Float64) / pl.col("90s")).alias("shots_created_per_90"),
    (pl.col("Goal Assists").cast(pl.Float64) / pl.col("90s")).alias("assists_per_90"),
    (pl.col("Assists (Intentional)").cast(pl.Float64) / pl.col("90s")).alias("intentional_assists_per_90"),
    (pl.col("Successful Dribbles").cast(pl.Float64) / pl.col("90s")).alias("successful_dribbles_per_90"),
    (pl.col("Aerial Duels won").cast(pl.Float64) / pl.col("90s")).alias("aerial_duels_won_per_90"),
    (pl.col("Goals").cast(pl.Float64) / (pl.col("Total Shots").cast(pl.Float64) + 1e-5)).alias("conversion_rate"),
    (pl.col("Shots On Target ( inc goals )").cast(pl.Float64) / (pl.col("Total Shots").cast(pl.Float64) + 1e-5)).alias("shot_accuracy"),
    (pl.col("Total Big Chances Scored").cast(pl.Float64) / (pl.col("Total Big Chances Scored").cast(pl.Float64) + pl.col("Total Big Chances Missed").cast(pl.Float64) + 1e-5)).alias("pct_big_chances_scored")
])

####### Una vez nada mas ####

fw_features.write_parquet('data/raw/forwards.parquet')

#############################


for_cols = [
    "total_shots_per_90", "shots_on_target_per_90", "shots_off_target_per_90", 
    "goals_per_90", "goals_openplay_per_90", "goals_inside_box_per_90", 
    "big_chances_scored_per_90", "big_chances_missed_per_90", "box_touches_per_90", 
    "key_passes_per_90", "shots_created_per_90", "assists_per_90", 
    "intentional_assists_per_90", "successful_dribbles_per_90", "aerial_duels_won_per_90", 
    "conversion_rate", "shot_accuracy", "pct_big_chances_scored"
]

#forwards = fw_features.to_pandas()
forwards = pd.read_parquet('data/raw/forwards.parquet')

#-------------------------------------------------------------------

player_forwards = forwards['nombre'].astype(str)
team_forwards = forwards['equipo'].astype(str)
X_for = forwards[for_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)
for_scaler = StandardScaler(with_mean = True, with_std = True)
X_for_scaled = for_scaler.fit_transform(X_for.values)


ks = list(range(2, 11))
elbow_for_res = [kmeans_wss(k,X_for_scaled) for k in ks]

df_res_for = pd.DataFrame({
    'k': ks,
    'wss': elbow_for_res,
    'pos': 'fw'
    })

sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_res_for, x="k", y="wss", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_res_for["k"])
plt.title("Elbow Method for Optimal k", fontweight="bold", pad=15)
plt.show()

sil_for_val = [silhouette_for_k(k, X_for_scaled) for k in ks]

df_sil_for = pd.DataFrame({
    'k': ks,
    'sil': sil_for_val,
    'pos': 'fw'
    })

sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_sil_for, x="k", y="sil", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_sil_for["k"])
plt.title("Silhouette Score for K", fontweight="bold", pad=15)
plt.show()

## En este caso el optimal k sera 5 

for_kmeans = KMeans(
        n_clusters = 4,
        n_init = 25,
        max_iter = 100,
        random_state = 69,
        algorithm = 'lloyd'
        ).fit(X_for_scaled)

forwards['cluster'] = for_kmeans.labels_

forwards['cluster'].value_counts()

forward_clusters = forwards[['nombre', 'cluster']].sort_values(['cluster'])

print(forward_clusters.to_string(index = False))

barca_forwards = forwards[forwards['equipo'] == 'FC Barcelona']['nombre'].to_list()
forwards_dfs = []
for player in barca_forwards:
    player_idx = forwards[forwards['nombre'] == player].index[0]
    player_cluster = forwards.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    target_player_df = forwards.loc[[player_idx]].copy()
    target_player_df['Statistic_compatibility'] = 0.0  
    same_cluster_mask = (forwards['cluster'] == player_cluster) & (forwards['nombre'] != player)
    cluster_mates = forwards[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    dfs = forwards.loc[cluster_mates.index].copy()
    cluster_mates['distance_to_target'] = distances
    dfs['Statistic_compatibility'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    dfs_sorted = dfs.sort_values('Statistic_compatibility').head(5)
    radar_cols = ['nombre', 'equipo', 'cluster', 'Statistic_compatibility']+for_cols  
    matches_sliced = dfs_sorted[radar_cols]
    target_sliced = target_player_df[radar_cols]
    radar_ready_df = pd.concat([target_sliced, matches_sliced], ignore_index=True)
    forwards_dfs.append(radar_ready_df)
    print(f"\nResult for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['nombre', 'equipo', 'distance_to_target']].to_string(index=False))



wingers = ['shots_on_target_per_90', 'goals_per_90', 'key_passes_per_90', 'shots_created_per_90','assists_per_90', 'successful_dribbles_per_90', 'total_shots_per_90', 'shots_off_target_per_90', 'big_chances_scored_per_90', 'big_chances_missed_per_90', 'shot_accuracy']
striker = [
    "total_shots_per_90",
    "shots_on_target_per_90",
    "shots_off_target_per_90",
    "goals_per_90",
    "goals_openplay_per_90",
    "goals_inside_box_per_90",
    "big_chances_scored_per_90",
    "big_chances_missed_per_90",
    "conversion_rate",
    "shot_accuracy",
]


plot_player_radar_scaled(forwards_dfs, 5, feature_cols = striker, full_dataset = forwards)

forwards_trial = [
        {
            "dfs_list": forwards_dfs,
            "full_dataset": forwards,
            "pos_label": "FW",
            "cluster_profile_map": {
                0: wingers,
                1: striker
                }
            },
        {
            "dfs_list": midfield_dfs,
            "full_dataset": midfield,
            "pos_label": "MF",
            "cluster_profile_map": {
                1: defensive_mid,
                2: offensive_mid
                }
            },
        {
            "dfs_list": defense_dfs,
            "full_dataset": defense,
            "pos_label": "DF",
            "cluster_profile_map": {
                0: centre_back,
                1: full_backs,
                2: defense_2
                }
            },
        {
            "dfs_list": keeper_dfs,
            "full_dataset": keeper,
            "pos_label": "GK",
            "cluster_profile_map": {
                2: keeper_0,
                4: keeper_0,
                1: keeper_0
                }
            }
        ]

generate_cluster_specific_ui_json(forwards_trial, "data/processed/radar_trial.json")
#--------------------------------------

centers_transposed = for_kmeans.cluster_centers_.T

forward_results = pd.DataFrame({
    'Feature': for_cols,
    'Cluster 0': centers_transposed[:, 0],
    'Cluster 1': centers_transposed[:, 1],
    'Cluster 2': centers_transposed[:, 2],
    'Cluster 3': centers_transposed[:, 3],
})

print(forward_results)


### Miremos los resultados

forward_results = forward_results.set_index("Feature")
fig, ax = plt.subplots(figsize=(9, 6.5))
sns.heatmap(
    forward_results, 
    annot=True,              
    fmt=".2f",               
    cmap="RdBu_r",           
    center=0,                
    robust=True,             
    linewidths=0.75,          
    cbar_kws={'label': 'Standard Deviations from Mean ($\sigma$)'},
    ax=ax
)
ax.set_title("Cluster Behavioral Profiles", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Clusters", fontsize=12, labelpad=10)
ax.set_ylabel("Features", fontsize=12, labelpad=10)
plt.tight_layout()
plt.show()


#--------------------------------------------------------------------------
### Mediocampistas
midfield = df.filter(( pl.col('posicion') == 'Midfielder' ) & (pl.col('Time Played') > 450.0))

mf_features = midfield.with_columns([
    # Per-90 Metrics
    (pl.col("Total Passes").cast(pl.Float64) / pl.col("90s")).alias("total_passes_per_90"),
    (pl.col("Successful Long Passes").cast(pl.Float64) / pl.col("90s")).alias("successful_long_passes_per_90"),
    (pl.col("Forward Passes").cast(pl.Float64) / pl.col("90s")).alias("forward_passes_per_90"),
    (pl.col("Successful Passes Opposition Half").cast(pl.Float64) / pl.col("90s")).alias("successful_passes_opp_half_per_90"),
    (pl.col("Shots On Target ( inc goals )").cast(pl.Float64) / pl.col("90s")).alias("shots_on_target_per_90"),
    (pl.col("Goals").cast(pl.Float64) / pl.col("90s")).alias("goals_per_90"),
    (pl.col("Goal Assists").cast(pl.Float64) / pl.col("90s")).alias("assists_per_90"),
    (pl.col("Through balls").cast(pl.Float64) / pl.col("90s")).alias("through_balls_per_90"),
    (pl.col("Progressive Carries").cast(pl.Float64) / pl.col("90s")).alias("progressive_carries_per_90"),
    (pl.col("Key Passes (Attempt Assists)").cast(pl.Float64) / pl.col("90s")).alias("key_passes_per_90"),
    (pl.col("Shots Created").cast(pl.Float64) / pl.col("90s")).alias("shots_created_per_90"),
    (pl.col("Tackles Won").cast(pl.Float64) / pl.col("90s")).alias("tackles_won_per_90"),
    (pl.col("Interceptions").cast(pl.Float64) / pl.col("90s")).alias("interceptions_per_90"),
    (pl.col("Recoveries").cast(pl.Float64) / pl.col("90s")).alias("recoveries_per_90"),
    (pl.col("Total Touches In Opposition Box").cast(pl.Float64) / pl.col("90s")).alias("box_touches_per_90"),
    (pl.col("Final Third Touches").cast(pl.Float64) / pl.col("90s")).alias("final_third_touches_per_90"),
    (pl.col("Total Shots").cast(pl.Float64) / pl.col("90s")).alias("total_shots_per_90"),
    (pl.col("Total Big Chances Created").cast(pl.Float64) / pl.col("90s")).alias("big_chances_created_per_90"),
    # Ratios (Using Total Successful / Unsuccessful Passes columns directly from schema)
    (pl.col("Successful Passes Opposition Half").cast(pl.Float64) / (pl.col("Successful Passes Opposition Half").cast(pl.Float64) + pl.col("Unsuccessful Passes Opposition Half").cast(pl.Float64) + 1e-5)).alias("pct_pass_accuracy_opp_half"),
    (pl.col("Total Successful Passes ( Excl Crosses & Corners ) ").cast(pl.Float64) / (pl.col("Total Passes").cast(pl.Float64) + 1e-5)).alias("pct_pass_accuracy"),
])

#-------------------------------------------------------
mf_features.write_parquet('data/raw/midfielders.parquet')
#-------------------------------------------------------

mid_cols = [
    "total_passes_per_90", "successful_long_passes_per_90", "forward_passes_per_90", 
    "successful_passes_opp_half_per_90", "through_balls_per_90", "progressive_carries_per_90", 
    "key_passes_per_90", "shots_created_per_90", "tackles_won_per_90", 
    "interceptions_per_90", "recoveries_per_90", "box_touches_per_90", 
    "final_third_touches_per_90", "total_shots_per_90", "big_chances_created_per_90", 
    "pct_pass_accuracy", "pct_pass_accuracy_opp_half", "goals_per_90", "shots_on_target_per_90", 'assists_per_90'
]

midfield = pd.read_parquet('data/raw/midfielders.parquet')

player_midfield = midfield['nombre'].astype(str)
team_midfield = midfield['equipo'].astype(str)
X_for = midfield[mid_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)


###Normalizamos el Standard Deviation a una sola escala
mid_scaler = StandardScaler(with_mean = True, with_std = True)
X_for_scaled = mid_scaler.fit_transform(X_for.values)


#### El número máximo de clusters es 10
ks = list(range(2, 11))
elbow_for_res = [kmeans_wss(k,X_for_scaled) for k in ks]
df_res_for = pd.DataFrame({
   'k': ks,
   'wss': elbow_for_res,
   'pos': 'mf'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_res_for, x="k", y="wss", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_res_for["k"])
plt.title("Elbow Method for Optimal k", fontweight="bold", pad=15)
plt.show()

sil_for_val = [silhouette_for_k(k, X_for_scaled) for k in ks]
df_sil_for = pd.DataFrame({
   'k': ks,
   'sil': sil_for_val,
   'pos': 'mf'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_sil_for, x="k", y="sil", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_sil_for["k"])
plt.title("Silhouette Score for K", fontweight="bold", pad=15)
plt.show()

## En este caso el número optimo de k es 3
for_kmeans = KMeans(
       n_clusters = 3,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)


midfield['cluster'] = for_kmeans.labels_


midfield['cluster'].value_counts()

barca_midfield = midfield[midfield['equipo'] == 'FC Barcelona']['nombre'].to_list()
midfield_dfs = []
for player in barca_midfield:
    player_idx = midfield[midfield['nombre'] == player].index[0]
    player_cluster = midfield.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    target_player_df = midfield.loc[[player_idx]].copy()
    target_player_df['Statistic_compatibility'] = 0.0  
    same_cluster_mask = (midfield['cluster'] == player_cluster) & (midfield['nombre'] != player)
    cluster_mates = midfield[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    dfs = midfield.loc[cluster_mates.index].copy()
    cluster_mates['distance_to_target'] = distances
    dfs['Statistic_compatibility'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    dfs_sorted = dfs.sort_values('Statistic_compatibility').head(5)
    radar_cols = ['nombre', 'equipo', 'cluster', 'Statistic_compatibility']+mid_cols  
    matches_sliced = dfs_sorted[radar_cols]
    target_sliced = target_player_df[radar_cols]
    radar_ready_df = pd.concat([target_sliced, matches_sliced], ignore_index=True)
    midfield_dfs.append(radar_ready_df)
    print(f"\nResult for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['nombre', 'equipo', 'distance_to_target']].to_string(index=False))


midfield_clusters = midfield[['Player', 'cluster']].sort_values(['cluster'])
print(midfield_clusters.to_string(index = False))


centers_transposed = for_kmeans.cluster_centers_.T


midfield_results = pd.DataFrame({
   'Feature': mid_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2],
})


#-----------------------------------

offensive_mid = [
    "box_touches_per_90",
    "final_third_touches_per_90",
    "total_shots_per_90",
    "big_chances_created_per_90",
    "through_balls_per_90",
    "progressive_carries_per_90",
    "key_passes_per_90",
    "shots_created_per_90",
    "shots_on_target_per_90",
    "goals_per_90",
    "assists_per_90",
]
defensive_mid = [
    "total_passes_per_90",
    "successful_long_passes_per_90",
    "forward_passes_per_90",
    "successful_passes_opp_half_per_90",
    "progressive_carries_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "recoveries_per_90",
    "pct_pass_accuracy",
    "pct_pass_accuracy_opp_half",
    "key_passes_per_90",
    "shots_created_per_90",
]


plot_player_radar_scaled(midfield_dfs, 5, feature_cols = defensive_mid, full_dataset = midfield)

#-----------------------------------


print(midfield_results)

### Miramos los resultados
midfield_results = midfield_results.set_index("Feature")
fig, ax = plt.subplots(figsize=(9, 6.5))
sns.heatmap(
   midfield_results,
   annot=True,             
   fmt=".2f",              
   cmap="RdBu_r",          
   center=0,               
   robust=True,            
   linewidths=0.75,         
   cbar_kws={'label': 'Standard Deviations from Mean ($\sigma$)'},
   ax=ax
)
ax.set_title("Cluster Behavioral Profiles", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Clusters", fontsize=12, labelpad=10)
ax.set_ylabel("Features", fontsize=12, labelpad=10)
plt.tight_layout()
plt.show()

#--------------------------------------------------------------------------
### Defensas
df = df.with_columns((pl.col('Time Played') / 90.0).alias("90s"))


defense = df.filter(( pl.col('posicion') == 'Defender' ) & (pl.col('Time Played') > 450.0))


df_features = defense.with_columns([
    # Per-90 Metrics
    (pl.col("Total Clearances").cast(pl.Float64) / pl.col("90s")).alias("clearances_per_90"),
    (pl.col("Total Tackles").cast(pl.Float64) / pl.col("90s")).alias("tackles_per_90"),
    (pl.col("Tackles Won").cast(pl.Float64) / pl.col("90s")).alias("tackles_won_per_90"),
    (pl.col("Final Third Touches").cast(pl.Float64) / pl.col("90s")).alias("final_third_touches_per_90"),
    (pl.col("Goal Assists").cast(pl.Float64) / pl.col("90s")).alias("assists_per_90"),
    (pl.col("Total Successful Passes ( Excl Crosses & Corners ) ").cast(pl.Float64) / (pl.col("Total Passes").cast(pl.Float64) + 1e-5)).alias("pct_pass_accuracy"),
    (pl.col("Tackles Lost").cast(pl.Float64) / pl.col("90s")).alias("tackles_lost_per_90"),
    (pl.col("Interceptions").cast(pl.Float64) / pl.col("90s")).alias("interceptions_per_90"),
    (pl.col("Blocks").cast(pl.Float64) / pl.col("90s")).alias("blocks_per_90"),
    (pl.col("Blocked Shots").cast(pl.Float64) / pl.col("90s")).alias("blocked_shots_per_90"),
    (pl.col("Aerial Duels won").cast(pl.Float64) / pl.col("90s")).alias("aerial_duels_won_per_90"),
    (pl.col("Aerial Duels lost").cast(pl.Float64) / pl.col("90s")).alias("aerial_duels_lost_per_90"),
    (pl.col("Ground Duels won").cast(pl.Float64) / pl.col("90s")).alias("ground_duels_won_per_90"),
    (pl.col("Ground Duels lost").cast(pl.Float64) / pl.col("90s")).alias("ground_duels_lost_per_90"),
    (pl.col("Recoveries").cast(pl.Float64) / pl.col("90s")).alias("recoveries_per_90"),
    (pl.col("Successful Long Passes").cast(pl.Float64) / pl.col("90s")).alias("successful_long_passes_per_90"),
    (pl.col("Successful Crosses & Corners").cast(pl.Float64) / pl.col("90s")).alias("successful_crosses_corners_per_90"),
    (pl.col("Key Passes (Attempt Assists)").cast(pl.Float64) / pl.col("90s")).alias("key_passes_per_90"),
    # Absolutes (Rare Events)
    pl.col("Clearances Off the Line").cast(pl.Float64),
    pl.col("Goals").cast(pl.Float64).alias("raw_goals"),
    pl.col("Headed Goals").cast(pl.Float64).alias("raw_headed_goals"),
    # Ratios
    (pl.col("Aerial Duels won").cast(pl.Float64) / (pl.col("Aerial Duels won").cast(pl.Float64) + pl.col("Aerial Duels lost").cast(pl.Float64) + 1e-5)).alias("pct_aerial_duels_won"),
    (pl.col("Tackles Won").cast(pl.Float64) / (pl.col("Total Tackles").cast(pl.Float64) + 1e-5)).alias("pct_successful_tackles")
])


df_features.write_parquet('data/raw/defense.parquet')

defense = pd.read_parquet('data/raw/defense.parquet')
df_cols = [
    "clearances_per_90", "tackles_per_90", "tackles_won_per_90", "tackles_lost_per_90", 
    "interceptions_per_90", "blocks_per_90", "blocked_shots_per_90", 
    "aerial_duels_won_per_90", "aerial_duels_lost_per_90", 
    "ground_duels_won_per_90", "ground_duels_lost_per_90", "recoveries_per_90", 
    "successful_long_passes_per_90", "successful_crosses_corners_per_90", "key_passes_per_90", 
    "Clearances Off the Line", "raw_goals", "raw_headed_goals", 
    "pct_aerial_duels_won", "pct_successful_tackles", "assists_per_90", "final_third_touches_per_90", "pct_pass_accuracy"
]

player_defense = defense['nombre'].astype(str)
team_defense = defense['equipo'].astype(str)
X_for = defense[df_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)


###Normalizamos el Standard Deviation a una sola escala
for_scaler = StandardScaler(with_mean = True, with_std = True)
X_for_scaled = for_scaler.fit_transform(X_for.values)


#### El número máximo de clusters es 10
ks = list(range(2, 11))
elbow_for_res = [kmeans_wss(k,X_for_scaled) for k in ks]
df_res_for = pd.DataFrame({
   'k': ks,
   'wss': elbow_for_res,
   'pos': 'df'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_res_for, x="k", y="wss", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_res_for["k"])
plt.title("Elbow Method for Optimal k", fontweight="bold", pad=15)
plt.show()


sil_for_val = [silhouette_for_k(k, X_for_scaled) for k in ks]
df_sil_for = pd.DataFrame({
   'k': ks,
   'sil': sil_for_val,
   'pos': 'df'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_sil_for, x="k", y="sil", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_sil_for["k"])
plt.title("Silhouette Score for K", fontweight="bold", pad=15)
plt.show()


## En este caso el optimal k sera 3
for_kmeans = KMeans(
       n_clusters = 3,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)

defense['cluster'] = for_kmeans.labels_
defense['cluster'].value_counts()

barca_defense = defense[defense['equipo'] == 'FC Barcelona']['nombre'].to_list()
defense_dfs = []
for player in barca_defense:
    player_idx = defense[defense['nombre'] == player].index[0]
    player_cluster = defense.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    target_player_df = defense.loc[[player_idx]].copy()
    target_player_df['Statistic_compatibility'] = 0.0  
    same_cluster_mask = (defense['cluster'] == player_cluster) & (defense['nombre'] != player)
    cluster_mates = defense[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    dfs = defense.loc[cluster_mates.index].copy()
    cluster_mates['distance_to_target'] = distances
    dfs['Statistic_compatibility'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    dfs_sorted = dfs.sort_values('Statistic_compatibility').head(5)
    radar_cols = ['nombre', 'equipo', 'cluster', 'Statistic_compatibility']+df_cols 
    matches_sliced = dfs_sorted[radar_cols]
    target_sliced = target_player_df[radar_cols]
    radar_ready_df = pd.concat([target_sliced, matches_sliced], ignore_index=True)
    defense_dfs.append(radar_ready_df)
    print(f"\nResult for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['nombre', 'equipo', 'distance_to_target']].to_string(index=False))


##-----------------------------------
defense_2 = [
    "tackles_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "blocked_shots_per_90",
    "aerial_duels_won_per_90",
    "aerial_duels_lost_per_90",
    "ground_duels_won_per_90",
    "ground_duels_lost_per_90",
    "recoveries_per_90",
    "successful_crosses_corners_per_90",
    "key_passes_per_90",
    "assists_per_90",
    "final_third_touches_per_90",
    "pct_pass_accuracy"
]
centre_back = [
    "clearances_per_90",
    "tackles_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "blocks_per_90",
    "blocked_shots_per_90",
    "aerial_duels_won_per_90",
    "aerial_duels_lost_per_90",
    "recoveries_per_90",
    "successful_long_passes_per_90",
    "raw_goals",
    "raw_headed_goals",
    "pct_aerial_duels_won",
    "pct_pass_accuracy"
]
full_backs = [
    "tackles_per_90",  
    "tackles_won_per_90",
    "blocked_shots_per_90",
    "ground_duels_won_per_90",
    "ground_duels_lost_per_90",
    "recoveries_per_90",
    "successful_crosses_corners_per_90",
    "key_passes_per_90",
    "raw_goals",
    "assists_per_90",
    "final_third_touches_per_90",
    "pct_pass_accuracy"
]

##-----------------------------------

plot_player_radar_scaled(defense_dfs, 5, feature_cols = defense_2, full_dataset = defense)

defense_clusters = defense[['Player', 'cluster']].sort_values(['cluster'])
print(defense_clusters.to_string(index = False))

centers_transposed = for_kmeans.cluster_centers_.T


defense_results = pd.DataFrame({
   'Feature': df_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2],
})


print(defense_results)


### Miramos los resultados
defense_results = defense_results.set_index("Feature")
fig, ax = plt.subplots(figsize=(9, 6.5))
sns.heatmap(
   defense_results,
   annot=True,             
   fmt=".2f",              
   cmap="RdBu_r",          
   center=0,               
   robust=True,            
   linewidths=0.75,         
   cbar_kws={'label': 'Standard Deviations from Mean ($\sigma$)'},
   ax=ax
)
ax.set_title("Cluster Behavioral Profiles", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Clusters", fontsize=12, labelpad=10)
ax.set_ylabel("Features", fontsize=12, labelpad=10)
plt.tight_layout()
plt.show()


#--------------------------------------------------------------------------
### Porteros


keeper = df.filter(( pl.col('posicion') == 'Goalkeeper' ) & (pl.col('Time Played') > 450.0))

gk_features = keeper.with_columns([
    # Per-90 Metrics
    (pl.col("Saves Made").cast(pl.Float64) / pl.col("90s")).alias("saves_per_90"),
    (pl.col("Saves Made from Inside Box").cast(pl.Float64) / pl.col("90s")).alias("saves_inside_box_per_90"),
    (pl.col("Saves Made from Outside Box").cast(pl.Float64) / pl.col("90s")).alias("saves_outside_box_per_90"),
    (pl.col("Goals Conceded").cast(pl.Float64) / pl.col("90s")).alias("goals_conceded_per_90"),
    (pl.col("Goals Conceded Inside Box").cast(pl.Float64) / pl.col("90s")).alias("goals_conceded_inside_per_90"),
    (pl.col("Goals Conceded Outside Box").cast(pl.Float64) / pl.col("90s")).alias("goals_conceded_outside_per_90"),
    (pl.col("GK Successful Distribution").cast(pl.Float64) / pl.col("90s")).alias("gk_success_dist_per_90"),
    (pl.col("GK Unsuccessful Distribution").cast(pl.Float64) / pl.col("90s")).alias("gk_unsuccess_dist_per_90"),
    (pl.col("Goal Kicks").cast(pl.Float64) / pl.col("90s")).alias("goal_kicks_per_90"),
    (pl.col("Punches").cast(pl.Float64) / pl.col("90s")).alias("punches_per_90"),
    (pl.col("Catches").cast(pl.Float64) / pl.col("90s")).alias("catches_per_90"),
    (pl.col("Drops").cast(pl.Float64) / pl.col("90s")).alias("drops_per_90"),
    (pl.col("Crosses not Claimed").cast(pl.Float64) / pl.col("90s")).alias("crosses_not_claimed_per_90"),
    (pl.col("Goalkeeper Smother").cast(pl.Float64) / pl.col("90s")).alias("smothers_per_90"),
    # Absolutes (Unscaled)
    pl.col("Clean Sheets").cast(pl.Float64),
    pl.col("Penalties Faced").cast(pl.Float64),
    pl.col("Penalties Saved").cast(pl.Float64),
    pl.col("Saves from Penalty").cast(pl.Float64),
    # Ratios
    (pl.col("Saves Made").cast(pl.Float64) / (pl.col("Saves Made").cast(pl.Float64) + pl.col("Goals Conceded").cast(pl.Float64) + 1e-5)).alias("save_percentage"),
    (pl.col("GK Successful Distribution").cast(pl.Float64) / (pl.col("GK Successful Distribution").cast(pl.Float64) + pl.col("GK Unsuccessful Distribution").cast(pl.Float64) + 1e-5)).alias("pct_successful_distribution")
])


gk_features.write_parquet('data/raw/goalkeeper.parquet')

keeper = pd.read_parquet('data/raw/goalkeeper.parquet')


gk_cols = [
    "saves_per_90", "saves_inside_box_per_90", "saves_outside_box_per_90", 
    "goals_conceded_per_90", "goals_conceded_inside_per_90", "goals_conceded_outside_per_90", 
    "gk_success_dist_per_90", "gk_unsuccess_dist_per_90", "goal_kicks_per_90", 
    "punches_per_90", "catches_per_90", "drops_per_90", 
    "crosses_not_claimed_per_90", "smothers_per_90", 
    "Clean Sheets", "Penalties Faced", "Penalties Saved", "Saves from Penalty", 
    "save_percentage", "pct_successful_distribution"
]


player_keeper = keeper['nombre'].astype(str)
team_keeper = keeper['equipo'].astype(str)

#Acá tendremos que agregar stats por 90mins

X_for = keeper[gk_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)


###Normalizamos el Standard Deviation a una sola escala
for_scaler = StandardScaler(with_mean = True, with_std = True)
X_for_scaled = for_scaler.fit_transform(X_for.values)


ks = list(range(2, 11))
elbow_for_res = [kmeans_wss(k,X_for_scaled) for k in ks]
df_res_for = pd.DataFrame({
   'k': ks,
   'wss': elbow_for_res,
   'pos': 'gk'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_res_for, x="k", y="wss", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_res_for["k"])
plt.title("Elbow Method for Optimal k", fontweight="bold", pad=15)
plt.show()


sil_for_val = [silhouette_for_k(k, X_for_scaled) for k in ks]
df_sil_for = pd.DataFrame({
   'k': ks,
   'sil': sil_for_val,
   'pos': 'gk'
   })
sns.set_theme(style="whitegrid")
plt.figure(figsize=(7, 4.5))
sns.lineplot(data=df_sil_for, x="k", y="sil", marker="o", linewidth=2.5, markersize=8)
plt.xticks(df_sil_for["k"])
plt.title("Silhouette Score for K", fontweight="bold", pad=15)
plt.show()


## En este caso el optimal k sera 6
for_kmeans = KMeans(
       n_clusters = 6,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)


keeper['cluster'] = for_kmeans.labels_
keeper['cluster'].value_counts()

barca_keeper = keeper[keeper['equipo'] == 'FC Barcelona']['nombre'].to_list()
keeper_dfs = []
for player in barca_keeper:
    player_idx = keeper[keeper['nombre'] == player].index[0]
    player_cluster = keeper.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    target_player_df = keeper.loc[[player_idx]].copy()
    target_player_df['Statistic_compatibility'] = 0.0  
    same_cluster_mask = (keeper['cluster'] == player_cluster) & (keeper['nombre'] != player)
    cluster_mates = keeper[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    dfs = keeper.loc[cluster_mates.index].copy()
    cluster_mates['distance_to_target'] = distances
    dfs['Statistic_compatibility'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    dfs_sorted = dfs.sort_values('Statistic_compatibility').head(5)
    radar_cols = ['nombre', 'equipo', 'cluster', 'Statistic_compatibility']+gk_cols
    matches_sliced = dfs_sorted[radar_cols]
    target_sliced = target_player_df[radar_cols]
    radar_ready_df = pd.concat([target_sliced, matches_sliced], ignore_index=True)
    keeper_dfs.append(radar_ready_df)
    print(f"\nResult for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['nombre', 'equipo', 'distance_to_target']].to_string(index=False))


#-----------------------------
keeper_0 = [
    "saves_per_90",
    "goals_conceded_per_90",
    "goals_conceded_inside_per_90",
    "goals_conceded_outside_per_90",
    "punches_per_90",
    "catches_per_90",
    "drops_per_90",
    "Penalties Faced",
    "Penalties Saved",
    "Clean Sheets",
    "save_percentage"
]

#-----------------------------


keeper_clusters = keeper[['Player', 'cluster']].sort_values(['cluster'])
print(keeper_clusters.to_string(index = False))


centers_transposed = for_kmeans.cluster_centers_.T
keeper_results = pd.DataFrame({
   'Feature': gk_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2], 
   'Cluster 3': centers_transposed[:, 3],
   'Cluster 4': centers_transposed[:, 4],
   'Cluster 5': centers_transposed[:, 5]
})
print(keeper_results)

### Miramos los resultados
keeper_results = keeper_results.set_index("Feature")
fig, ax = plt.subplots(figsize=(9, 6.5))
sns.heatmap(
   keeper_results,
   annot=True,             
   fmt=".2f",              
   cmap="RdBu_r",          
   center=0,               
   robust=True,            
   linewidths=0.75,         
   cbar_kws={'label': 'Standard Deviations from Mean ($\sigma$)'},
   ax=ax
)
ax.set_title("Cluster Behavioral Profiles", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Clusters", fontsize=12, labelpad=10)
ax.set_ylabel("Features", fontsize=12, labelpad=10)
plt.tight_layout()
plt.show()


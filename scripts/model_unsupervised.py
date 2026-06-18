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

# Function to see the goodness of the K
## we will use 

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

forwards = fw_features.to_pandas()

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

for player in barca_forwards:
    player_idx = forwards[forwards['nombre'] == player].index[0]
    player_cluster = forwards.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    same_cluster_mask = (forwards['cluster'] == player_cluster) & (forwards['nombre'] != player)
    cluster_mates = forwards[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    cluster_mates['distance_to_target'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    print(f"Result for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['nombre', 'equipo', 'distance_to_target']].to_string(index=False))





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
    "pct_pass_accuracy", "pct_pass_accuracy_opp_half"
]

midfield = mf_features.to_pandas()

player_midfield = midfield['nombre'].astype(str)
team_midfield = midfield['equipo'].astype(str)


X_for = midfield[mid_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)


###Normalizamos el Standard Deviation a una sola escala
mid_scaler = StandardScaler(with_mean = True, with_std = True)


X_for_scaled = mid_scaler.fit_transform(X_for.values)

pca =  PCA(n_components = 0.95, random_state = 69)

X_for_pca =  pca.fit_transform(X_for_scaled)

print(f"Original number of features: {X_for_scaled.shape[1]}")
print(f"Reduced number of features (PCs): {X_for_pca.shape[1]}")
print(f"Total variance explained: {np.sum(pca.explained_variance_ratio_):.2%}")

#### El número máximo de clusters es 10
ks = list(range(2, 11))
elbow_for_res = [kmeans_wss(k,X_for_pca) for k in ks]


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

sil_for_val = [silhouette_for_k(k, X_for_pca) for k in ks]


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

for player in barca_midfield:
    player_idx = midfield[midfield['nombre'] == player].index[0]
    player_cluster = midfield.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    same_cluster_mask = (midfield['cluster'] == player_cluster) & (midfield['nombre'] != player)
    cluster_mates = midfield[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    cluster_mates['distance_to_target'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    print(f"Result for {player}")
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
defense = players.filter(pl.col('Pos').is_in(['DF', 'DF,MF']))
defense = defense.to_pandas()
player_defense = defense['Player'].astype(str)
team_defense = defense['Squad'].astype(str)

for_cols = [
    'On-Off',
    '+/-90',
]

engineered = [
    'TklW',
    'Int',
    'Fls',
    'CrdY',
    'Crs',
    'Ast',
]

for col in engineered:
    defense[col + '/90'] = defense[col] / 90
    for_cols.append(col + '/90')

X_for = defense[for_cols].apply(pd.to_numeric, errors = 'coerce')
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


## En este caso el optimal k sera 4
for_kmeans = KMeans(
       n_clusters = 4,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)

defense['cluster'] = for_kmeans.labels_

defense['cluster'].value_counts()

barca_defense = defense[defense['Squad'] == 'Barcelona']['Player'].to_list()

for player in barca_defense:
    player_idx = defense[defense['Player'] == player].index[0]
    player_cluster = defense.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    same_cluster_mask = (defense['cluster'] == player_cluster) & (defense['Player'] != player)
    cluster_mates = defense[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    cluster_mates['distance_to_target'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    print(f"Result for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['Player', 'Squad', 'distance_to_target']].to_string(index=False))

defense_clusters = defense[['Player', 'cluster']].sort_values(['cluster'])

print(defense_clusters.to_string(index = False))

centers_transposed = for_kmeans.cluster_centers_.T


defense_results = pd.DataFrame({
   'Feature': for_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2],
   'Cluster 3': centers_transposed[:, 3]
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
keeper = players.filter(pl.col('Pos').is_in(['GK']))
keeper = keeper.to_pandas()
player_keeper = keeper['Player'].astype(str)
team_keeper = keeper['Squad'].astype(str)

for_cols = [
    'Save%',
    'GA90',
    'CS%',
    'PKsv',
    'SoTA',
    'GA',
    'W',
    'L',
]

#Acá tendremos que agregar stats por 90mins

X_for = keeper[for_cols].apply(pd.to_numeric, errors = 'coerce')
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


## En este caso el optimal k sera 3
for_kmeans = KMeans(
       n_clusters = 5,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)


keeper['cluster'] = for_kmeans.labels_


keeper['cluster'].value_counts()

barca_keeper = keeper[keeper['Squad'] == 'Barcelona']['Player'].to_list()
for player in barca_keeper:
    player_idx = keeper[keeper['Player'] == player].index[0]
    player_cluster = keeper.loc[player_idx, 'cluster']
    target_features = X_for_scaled[player_idx].reshape(1, -1)
    same_cluster_mask = (keeper['cluster'] == player_cluster) & (keeper['Player'] != player)
    cluster_mates = keeper[same_cluster_mask].copy()
    cluster_features = X_for_scaled[cluster_mates.index]
    distances = euclidean_distances(target_features, cluster_features).flatten()
    cluster_mates['distance_to_target'] = distances
    top_5_matches = cluster_mates.sort_values('distance_to_target').head(5)
    print(f"Result for {player}")
    print(f"Assigned Cluster: {player_cluster}")
    print(f"Top 5 closest stylistic matches within the cluster:")
    print(top_5_matches[['Player', 'Squad', 'distance_to_target']].to_string(index=False))

keeper_clusters = keeper[['Player', 'cluster']].sort_values(['cluster'])


print(keeper_clusters.to_string(index = False))


centers_transposed = for_kmeans.cluster_centers_.T


keeper_results = pd.DataFrame({
   'Feature': for_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2]
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


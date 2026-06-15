import polars as pl
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.metrics import silhouette_score as silo_score
import matplotlib.pyplot as plt
import seaborn as sns

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

players = (
        pl.scan_csv('data/raw/players_data-2025_2026.csv')
        ).collect()

## revisar duplicados

duplicated = players.filter(pl.col('Player').is_duplicated()).select(['Player', 'Squad'])


## Arreglar nacionalidad (Data Cleaning)

players = players.with_columns(
        pl.col('Nation').str.extract(r'([A-Z]+)')
        ).select(pl.all().exclude("Rk"))

# Create the different buckets for the different kmeans clustering


###### 

forwards = players.filter(pl.col('Pos').is_in(['FW', 'FW,MF']))
forwards = forwards.to_pandas()
player_forwards = forwards['Player'].astype(str)
team_forwards = forwards['Squad'].astype(str)
for_cols = [
        'G/SoT',      
        'SoT/90',     
        'G/Sh',       
        'Sh/90',      
        'G+A-PK',     
        'On-Off',    
    ]
engineered = [
        'G-PK',       
        'Ast',        
        'Fld',        
        'Off',        
    ]


for col in engineered:
    forwards[col + '/90'] = forwards[col] / 90
    for_cols.append(col + '/90')

X_for = forwards[for_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)

for_scaler = StandardScaler(with_mean = True, with_std = True)


X_for_scaled = for_scaler.fit_transform(X_for.values)




#### Finding the good k for forwards
#### Max number of clusters is 10
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
        n_clusters = 5,
        n_init = 25,
        max_iter = 100,
        random_state = 69,
        algorithm = 'lloyd'
        ).fit(X_for_scaled)

forwards['cluster'] = for_kmeans.labels_

forwards['cluster'].value_counts()

forward_clusters = forwards[['Player', 'cluster']].sort_values(['cluster'])

print(forward_clusters.to_string(index = False))
#### Checar que no esta Lamine, haremos cambios en esto


centers_transposed = for_kmeans.cluster_centers_.T

forward_results = pd.DataFrame({
    'Feature': for_cols,
    'Cluster 0': centers_transposed[:, 0],
    'Cluster 1': centers_transposed[:, 1],
    'Cluster 2': centers_transposed[:, 2],
    'Cluster 3': centers_transposed[:, 3],
    'Cluster 4': centers_transposed[:, 4]
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

midfield = players.filter(pl.col('Pos').is_in(['MF', 'MF,FW', 'MF,DF']))
midfield = midfield.to_pandas()
player_midfield = midfield['Player'].astype(str)
team_midfield = midfield['Squad'].astype(str)


### Variables  para esta posición
for_cols = [
    'G+A-PK',
    'On-Off',
]

engineered = [
    'Ast',
    'G-PK',
    'Crs',
    'TklW',
    'Int',
    'Fld',
    'Fls',
]

for col in engineered:
    midfield[col + '/90'] = midfield[col] / 90
    for_cols.append(col + '/90')

X_for = midfield[for_cols].apply(pd.to_numeric, errors = 'coerce')
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

## En este caso el número optimo de k es 5
for_kmeans = KMeans(
       n_clusters = 5,
       n_init = 25,
       max_iter = 100,
       random_state = 69,
       algorithm = 'lloyd'
       ).fit(X_for_scaled)


midfield['cluster'] = for_kmeans.labels_


midfield['cluster'].value_counts()


midfield_clusters = midfield[['Player', 'cluster']].sort_values(['cluster'])


print(midfield_clusters.to_string(index = False))


centers_transposed = for_kmeans.cluster_centers_.T


midfield_results = pd.DataFrame({
   'Feature': for_cols,
   'Cluster 0': centers_transposed[:, 0],
   'Cluster 1': centers_transposed[:, 1],
   'Cluster 2': centers_transposed[:, 2],
   'Cluster 3': centers_transposed[:, 3],
   'Cluster 4': centers_transposed[:, 4]
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


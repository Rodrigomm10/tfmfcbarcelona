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
        pl.scan_csv('data\\raw\\players_data-2025_2026.csv')
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
#### Max number of clusters is 8
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
plt.xticks(df_pd["k"])
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


### MIremos los resultados

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

########

midfield = players.filter(pl.col('Pos').is_in(['MF', 'MF,FW', 'MF,DF']))
### para los mediocampistas


midfield = players.filter(pl.col('Pos').is_in(['MF', 'MF,FW', 'MF,DF']))

midfield = midfield.to_pandas()

player_midfield = midfield['Player'].astype(str)
team_midfield = midfield['Squad'].astype(str)


### Variables numéricas para esta posición (recuerdese que hice las normales que algunas ya están /90 y las otras que dividimos para convertir /90
## Esto ya lo hizo para forwards y va a ser igual para todas las posiciones
## primero las que si están en las columnas

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


###Aacá me imagino que es para el cálculo del Standard Deviation o me perdí?
for_scaler = StandardScaler(with_mean = True, with_std = True)


X_for_scaled = for_scaler.fit_transform(X_for.values)


#### Acá ya seria de evaluar cuantos clusters hacemos, pero que imagino sería una prueba similar o con más clusters que los que hicimos antes para tener más grupos y que sea más exacta la selección del jugador con un perfil similar
for_kmeans = KMeans(
    n_clusters = 4,
        n_init = 25,
        max_iter = 100,
        random_state = 69,
        algorithm = 'lloyd'
        ).fit(X_for_scaled)

midfield['cluster'] = for_kmeans.labels_

midfield['cluster'].value_counts()

midfield_clusters = midfield[['Player', 'cluster']].sort_values(['cluster'])

print(midfield_clusters.to_string(index = False))


######

defense = players.filter(pl.col('Pos').is_in(['DF', 'DF,MF']))


### me quede tentado a seguir escribiendo todo en un cuadro para darle "RUN ALL"

##Ahora es lo mismo pero con los defensas

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
    defense[col + '/90') = defense[col] / 90
    for_cols.append(col + '/90')

X_for = defense[for_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)

for_scaler = StandardScaler(with_mean = True, with_std = True)


X_for_scaled = for_scaler.fit_transform(X_for.values)


#### Kmeans
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

######
keeper = players.filter(pl.col('Pos').is_in(['GK']))


##Los porteros para terminasssssshhhhh que ya tengo sueño 

keeper = players.filter(pl.col('Pos').is_in(['GK']))

keeper = keeper.to_pandas()

player_keeper = keeper['Player'].astype(str)
team_keeper = keeper['Squad'].astype(str)

for_cols = [
    'Save%',
    'GA90',
    'CS%',
    'PKsv',
]
## No creo que con estas 4 columnas es suficiente para evaluar a un portero, buscaré más métricas.

for col in engineered:
    keeper[col + '/90') = keeper[col] / 90
    for_cols.append(col + '/90')

X_for = defense[for_cols].apply(pd.to_numeric, errors = 'coerce')
X_for = X_for.fillna(0)

for_scaler = StandardScaler(with_mean = True, with_std = True)


X_for_scaled = for_scaler.fit_transform(X_for.values)


#### Kmeans
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


    
##Gracias por tomarse el tiempo de ayudarme y enseñarme Andresito! Aprendí más con usted en 1 semana que con esos chimps de profesores.
## A lo mejor necesito ir a Notre Dame para dejar de ser el único 'hijo idiota' que no fue capaz de ir a una universidad en Estados Unidos.

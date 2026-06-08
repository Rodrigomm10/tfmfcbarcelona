import polars as pl
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd


first = (
        pl.scan_csv('data\\raw\\players_data-2025_2026.csv')
        .head(5)
        )

first = first.collect()


first.glimpse()

top_5 = (
        pl.scan_csv('data\\raw\\players_data-2025_2026.csv')
        .select(pl.col( 'Comp' ).unique())
        )


top_5 = (
        pl.scan_csv('data\\raw\\players_data-2025_2026.csv')
        .select(pl.col( 'Comp' ).unique())
        )


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

## Numeric variables that we care about in forwards 

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


for_kmeans = KMeans(
        n_clusters = 4,
        n_init = 25,
        max_iter = 100,
        random_state = 69,
        algorithm = 'lloyd'
        ).fit(X_for_scaled)

forwards['cluster'] = for_kmeans.labels_

forwards['cluster'].value_counts()

forward_clusters = forwards[['Player', 'cluster']].sort_values(['cluster'])

print(forward_clusters.to_string(index = False))


centers_transposed = for_kmeans.cluster_centers_.T

forward_results = pl.DataFrame({
    'Feature': for_cols,
    'Cluster 0': centers_transposed[:, 0],
    'Cluster 1': centers_transposed[:, 1],
    'Cluster 2': centers_transposed[:, 2],
    'Cluster 3': centers_transposed[:, 3]
})

print(forward_results)

########


midfield = players.filter(pl.col('Pos').is_in(['MF', 'MF,FW', 'MF,DF']))

######

defense = players.filter(pl.col('Pos').is_in(['DF', 'DF,MF']))

######

keeper = players.filter(pl.col('Pos').is_in(['GK']))

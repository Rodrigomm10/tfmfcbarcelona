import polars as pl

#-----------------------------
# Arreglar los datos

forwards = (
        pl.scan_parquet('data/raw/forwards.parquet')
        .with_columns(
            pl.col('nombre')
            .str.replace(r"\.", "")
            .str.to_lowercase()
            .str.split(" ")
            )
        .with_columns([
            pl.col('nombre').list.get(0).str.slice(0,1).alias("first"),
            pl.col('nombre').list.get(-1).alias("last_name")
            ])
        )

player_ids = (
        pl.scan_csv('data/raw/players.csv')
        .select(['player_id', 'name'])
        .with_columns(
            pl.col('name')
            .str.to_lowercase()
            .str.split(" ")
            )
        .with_columns([
            pl.col('name').list.get(0).str.slice(0,1).alias("first"),
            pl.col('name').list.get(-1).alias("last_name")
            ])
        .unique(subset=['first', 'last_name'], keep = 'first')
        )

forwards = forwards.join(
        player_ids,
        on = ['first', 'last_name'],
        how = "inner"
        )


market_valuations = (
        pl.scan_csv('data/raw/player_valuations.csv', try_parse_dates = True)
        .join(
            forwards.select('player_id'),
            on = 'player_id',
            how = 'inner'
            )
        .sort('date')
        .unique(subset = ['player_id'], keep = 'last', maintain_order = True)
        )

final_plan = market_valuations.join(
        forwards,
        on = 'player_id',
        how = 'inner'
        )

forwards_df = final_plan.collect()

print(
    forwards_df.group_by("nombre")
    .count()
    .filter(pl.col("count") > 1)
    .sort("count", descending=True)
)


#----------------------------------------------------
# Listo para hacer modeling

valuations_forward = market_valuations.filter(pl.col('Pos').is_in(['FW', 'FW,MF']))
valuations_forward = market_valuations.to_pandas()

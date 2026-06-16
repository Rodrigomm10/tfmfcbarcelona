import polars as pl

#-----------------------------
# Arreglar los datos

players = (pl.scan_csv('data/raw/players_data-2025_2026.csv')
           .select(pl.col('Player').unique())).collect()

players = players['Player'].to_list()

players_ids = (
        pl.scan_csv('data/raw/players.csv')
        .filter(pl.col('name').is_in(players))
        .select(['player_id', 'name'])
        ).collect()

players_ids_list = players_ids['player_id'].to_list()


market_valuations = (
        pl.scan_csv('data/raw/player_valuations.csv', try_parse_dates = True)
        .filter(pl.col('player_id').is_in(players_ids_list))
        ).collect()

market_valuations = market_valuations.join(
        players_ids,
        on = 'player_id',
        how = 'inner'
        )

market_valuations = (
        market_valuations.sort('date')
        .unique(subset = ['name'], keep = 'last', maintain_order = True)
        )

stats = (pl.scan_csv('data/raw/players_data-2025_2026.csv')).collect()

market_valuations = market_valuations.join(
        stats,
        left_on = 'name',
        right_on = 'Player',
        how = 'inner'
        )


market_valuations.write_csv('data/raw/market_valuations_sl.csv')



#----------------------------------------------------
# Listo para hacer modeling

valuations_forward = market_valuations.filter(pl.col('Pos').is_in(['FW', 'FW,MF']))
valuations_forward = market_valuations.to_pandas()

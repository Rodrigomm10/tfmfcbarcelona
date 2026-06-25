import polars as pl

#-----------------------------
# Arreglar los datos

forwards = (
        pl.scan_parquet('data/raw/new_data.parquet')
        .with_columns(
            [
                pl.col('nombre')
                .str.replace(r"\.", "")
                .str.to_lowercase()
                .str.split(" "),
                pl.col('equipo')
                .str.to_lowercase()
                .str.split(" ")
                .list.get(0)
                .alias('club_key')
                ]
            )
        .with_columns([
            pl.col('nombre').list.get(0).str.slice(0,1).alias("first"),
            pl.col('nombre').list.get(-1).alias("last_name")
            ])
        )

player_ids = (
        pl.scan_csv('data/raw/players.csv')
        .select(['player_id', 'name', 'date_of_birth', 'current_club_name'])
        .with_columns(
            [
                pl.col('name')
                .str.to_lowercase()
                .str.split(" "),
                pl.col('current_club_name')
                .str.to_lowercase()
                .str.split(" ")
                .list.get(0)
                .alias("club_key")
                ]
            )
        .with_columns([
            pl.col('name').list.get(0).str.slice(0,1).alias("first"),
            pl.col('name').list.get(-1).alias("last_name")
            ])
        .unique(subset=['first', 'last_name', 'club_key'], keep = 'first')
        )

forwards = forwards.join(
        player_ids,
        on = ['first', 'last_name', 'club_key'],
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

data = final_plan.collect()

print(
    forwards_df.group_by("nombre")
    .len("count")
    .filter(pl.col("count") > 1)
    .sort("count", descending=True)
)


#----------------------------------------------------
# Listo para hacer modeling


data = data.unique(subset = ['nombre'], keep = 'first')


data = data.with_columns((pl.col('Time Played') / 90.0).alias("90s"))
data = data.with_columns([
    (pl.col("Shots On Target ( inc goals )").cast(pl.Float64) / pl.col("90s")).alias("shots_on_target_per_90"),
    (pl.col("Shots Off Target (inc woodwork)").cast(pl.Float64) / pl.col("90s")).alias("shots_off_target_per_90"),
    (pl.col("Total Shots").cast(pl.Float64) / pl.col("90s")).alias("total_shots_per_90"),
    (pl.col("Goals").cast(pl.Float64) / pl.col("90s")).alias("goals_per_90"),
    (pl.col("Goals Openplay").cast(pl.Float64) / pl.col("90s")).alias("goals_openplay_per_90"),
    (pl.col("Goals from Inside Box").cast(pl.Float64) / pl.col("90s")).alias("goals_inside_box_per_90"),
    (pl.col("Total Big Chances Scored").cast(pl.Float64) / pl.col("90s")).alias("big_chances_scored_per_90"),
    (pl.col("Total Big Chances Missed").cast(pl.Float64) / pl.col("90s")).alias("big_chances_missed_per_90"),
    (pl.col("Total Touches In Opposition Box").cast(pl.Float64) / pl.col("90s")).alias("box_touches_per_90"),
    (pl.col("Shots Created").cast(pl.Float64) / pl.col("90s")).alias("shots_created_per_90"),
    (pl.col("Assists (Intentional)").cast(pl.Float64) / pl.col("90s")).alias("intentional_assists_per_90"),
    (pl.col("Successful Dribbles").cast(pl.Float64) / pl.col("90s")).alias("successful_dribbles_per_90"),
    (pl.col("Aerial Duels won").cast(pl.Float64) / pl.col("90s")).alias("aerial_duels_won_per_90"),
    (pl.col("Goals").cast(pl.Float64) / (pl.col("Total Shots").cast(pl.Float64) + 1e-5)).alias("conversion_rate"),
    (pl.col("Shots On Target ( inc goals )").cast(pl.Float64) / (pl.col("Total Shots").cast(pl.Float64) + 1e-5)).alias("shot_accuracy"),
    (pl.col("Total Big Chances Scored").cast(pl.Float64) / (pl.col("Total Big Chances Scored").cast(pl.Float64) + pl.col("Total Big Chances Missed").cast(pl.Float64) + 1e-5)).alias("pct_big_chances_scored"),
    (pl.col("Total Passes").cast(pl.Float64) / pl.col("90s")).alias("total_passes_per_90"),
    (pl.col("Forward Passes").cast(pl.Float64) / pl.col("90s")).alias("forward_passes_per_90"),
    (pl.col("Successful Passes Opposition Half").cast(pl.Float64) / pl.col("90s")).alias("successful_passes_opp_half_per_90"),
    (pl.col("Through balls").cast(pl.Float64) / pl.col("90s")).alias("through_balls_per_90"),
    (pl.col("Progressive Carries").cast(pl.Float64) / pl.col("90s")).alias("progressive_carries_per_90"),
    (pl.col("Tackles Won").cast(pl.Float64) / pl.col("90s")).alias("tackles_won_per_90"),
    (pl.col("Recoveries").cast(pl.Float64) / pl.col("90s")).alias("recoveries_per_90"),
    (pl.col("Final Third Touches").cast(pl.Float64) / pl.col("90s")).alias("final_third_touches_per_90"),
    (pl.col("Total Big Chances Created").cast(pl.Float64) / pl.col("90s")).alias("big_chances_created_per_90"),
    (pl.col("Successful Passes Opposition Half").cast(pl.Float64) / (pl.col("Successful Passes Opposition Half").cast(pl.Float64) + pl.col("Unsuccessful Passes Opposition Half").cast(pl.Float64) + 1e-5)).alias("pct_pass_accuracy_opp_half"),
    (pl.col("Total Clearances").cast(pl.Float64) / pl.col("90s")).alias("clearances_per_90"),
    (pl.col("Total Tackles").cast(pl.Float64) / pl.col("90s")).alias("tackles_per_90"),
    (pl.col("Goal Assists").cast(pl.Float64) / pl.col("90s")).alias("assists_per_90"),
    (pl.col("Total Successful Passes ( Excl Crosses & Corners ) ").cast(pl.Float64) / (pl.col("Total Passes").cast(pl.Float64) + 1e-5)).alias("pct_pass_accuracy"),
    (pl.col("Tackles Lost").cast(pl.Float64) / pl.col("90s")).alias("tackles_lost_per_90"),
    (pl.col("Interceptions").cast(pl.Float64) / pl.col("90s")).alias("interceptions_per_90"),
    (pl.col("Blocks").cast(pl.Float64) / pl.col("90s")).alias("blocks_per_90"),
    (pl.col("Blocked Shots").cast(pl.Float64) / pl.col("90s")).alias("blocked_shots_per_90"),
    (pl.col("Aerial Duels lost").cast(pl.Float64) / pl.col("90s")).alias("aerial_duels_lost_per_90"),
    (pl.col("Ground Duels won").cast(pl.Float64) / pl.col("90s")).alias("ground_duels_won_per_90"),
    (pl.col("Ground Duels lost").cast(pl.Float64) / pl.col("90s")).alias("ground_duels_lost_per_90"),
    (pl.col("Successful Long Passes").cast(pl.Float64) / pl.col("90s")).alias("successful_long_passes_per_90"),
    (pl.col("Successful Crosses & Corners").cast(pl.Float64) / pl.col("90s")).alias("successful_crosses_corners_per_90"),
    (pl.col("Key Passes (Attempt Assists)").cast(pl.Float64) / pl.col("90s")).alias("key_passes_per_90"),
    pl.col("Clearances Off the Line").cast(pl.Float64),
    pl.col("Goals").cast(pl.Float64).alias("raw_goals"),
    pl.col("Headed Goals").cast(pl.Float64).alias("raw_headed_goals"),
    (pl.col("Aerial Duels won").cast(pl.Float64) / (pl.col("Aerial Duels won").cast(pl.Float64) + pl.col("Aerial Duels lost").cast(pl.Float64) + 1e-5)).alias("pct_aerial_duels_won"),
    (pl.col("Tackles Won").cast(pl.Float64) / (pl.col("Total Tackles").cast(pl.Float64) + 1e-5)).alias("pct_successful_tackles")
])

cols = [
    "market_value_in_eur",  
    "date",  
    "date_of_birth",  
    "liga",  
    "temporada",  
    "90s",  
    "goals_per_90",
    "total_shots_per_90",
    "Winning Goal",
    "Total Big Chances Missed",
    "assists_per_90",
    "key_passes_per_90",
    "Total Big Chances Created",
    "Second Goal Assists",
    "Total Successful Passes ( Excl Crosses & Corners ) ",
    "Successful Passes Opposition Half",
    "Progressive Carries",
    "Successful Dribbles",
    "Aerial Duels won",
    "Total Fouls Won",
    "Tackles Won",
    "Recoveries",
    "Foul Won Penalty",
]

data = (
        data.filter(pl.col('posicion') != 'Goalkeeper')
        .select(cols)
        .with_columns(
            ((pl.col('date') - pl.col('date_of_birth')).dt.total_days() /  365.25)
            .round(1)
            .alias('age')
            )
        .drop(['date', 'date_of_birth'])
        .drop_nulls()
        )

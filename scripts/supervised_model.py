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

data.write_parquet('data/raw/all_players_data.parquet')

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

data = pl.read_parquet('data/raw/all_players_data.parquet', try_parse_hive_dates = True)

data = (
    data.filter(pl.col("posicion") != "Goalkeeper")
    .select(cols)
    .with_columns(
        [
            pl.col("date").cast(pl.Date),
            pl.col("date_of_birth")
            .str.to_datetime(format="%Y-%m-%d %H:%M:%S")
            .cast(pl.Date),
        ]
    )
    .with_columns(
        ((pl.col("date") - pl.col("date_of_birth")).dt.total_days() / 365.25)
        .round(1)
        .alias("age")
    )
    .drop(["date", "date_of_birth"])
    .with_columns(pl.all().exclude("liga").fill_null(0))
)

data.write_parquet('data/raw/supervised_data.parquet')

# visualizaciones

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

data = pd.read_parquet('data/raw/supervised_data.parquet')
data.drop('temporada', axis = 1, inplace = True)

# Usamos el logaritmo para comprimir los valores de mercado hacia una distribution normal
data['log_market_val'] = np.log1p(data['market_value_in_eur'])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.kdeplot(
    x="market_value_in_eur", data=data, ax=axes[0], fill=True, color="crimson"
)
axes[0].set_title("Original Market Value (Highly Skewed)")
axes[0].set_xlabel("Market Value (€)")
sns.kdeplot(x="log_market_val", data=data, ax=axes[1], fill=True, color="royalblue")
axes[1].set_title("Log-Transformed Market Value (Bell Curve)")
axes[1].set_xlabel("Log(Market Value)")
plt.tight_layout()
plt.show()


sns.kdeplot(x = 'log_market_val', data = data, hue = 'liga')
plt.show()

sns.relplot(x = 'goals_per_90', y = 'log_market_val', data = data)
plt.show()

### partimos los datos

from sklearn.model_selection import train_test_split

train_data, test_data = train_test_split(
        data,
        test_size = 0.25,
        random_state = 69
        )


#### Usamos una regresion simple linear para empezar

import statsmodels.formula.api as smf

features = [
    "C(liga)",
    "Q('90s')",
    "goals_per_90",
    "total_shots_per_90",
    "Q('Winning Goal')",
    "Q('Total Big Chances Missed')",
    "assists_per_90",
    "key_passes_per_90",
    "Q('Total Big Chances Created')",
    "Q('Second Goal Assists')",
    "Q('Total Successful Passes ( Excl Crosses & Corners ) ')",
    "Q('Successful Passes Opposition Half')",
    "Q('Progressive Carries')",
    "Q('Successful Dribbles')",
    "Q('Aerial Duels won')",
    "Q('Total Fouls Won')",
    "Q('Tackles Won')",
    "Recoveries",
    "Q('Foul Won Penalty')",
    "age"
]


formula_1 = 'market_value_in_eur ~ ' + " + ".join(features)
formula_2 = 'log_market_val ~ ' + " + ".join(features)


model_1 = smf.ols(formula = formula_1, data = train_data).fit()
model_2 = smf.ols(formula = formula_2, data = train_data).fit()

model_1.summary()
model_2.summary()


# out of sample accuracy

from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
)

# evaluamos los valores fuera del sampleo

def get_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = mean_absolute_percentage_error(actual, predicted)
    print(f"MAE:  €{mae:,.2f}")  
    print(f"RMSE: €{rmse:,.2f}")
    print(f"MAPE: {mape:.2%}")
    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}


model1_pred = model_1.predict(test_data.drop(['market_value_in_eur', 'log_market_val'], axis = 1))
model2_pred = np.expm1(model_2.predict(test_data.drop(['market_value_in_eur', 'log_market_val'], axis = 1)))

model1_res = get_metrics(test_data['market_value_in_eur'], model1_pred)
model2_res = get_metrics(test_data['market_value_in_eur'], model2_pred)


# nos vemos al model general aditivo para curvas no lineales

from pygam import ExpectileGAM, LinearGAM, f, s
from sklearn.preprocessing import LabelEncoder

train_data['Second Goal Assists'] = pd.to_numeric( train_data['Second Goal Assists'], errors = 'coerce' )
train_data['Foul Won Penalty'] = pd.to_numeric( train_data['Foul Won Penalty'], errors = 'coerce' )

test_data['Second Goal Assists'] = pd.to_numeric( test_data['Second Goal Assists'], errors = 'coerce' )
test_data['Foul Won Penalty'] = pd.to_numeric( test_data['Foul Won Penalty'], errors = 'coerce' )

X_train_encoded = train_data.drop(['market_value_in_eur', 'log_market_val'], axis = 1)
y_train = train_data['log_market_val']

X_test_encoded = test_data.drop(['market_value_in_eur', 'log_market_val'], axis = 1)
y_test = test_data['market_value_in_eur']

le = LabelEncoder()

X_train_encoded['liga'] = le.fit_transform(X_train['liga'])
X_test_encoded['liga'] = le.transform(X_test['liga'])

terms = []
for col in X_train.columns:
    if col == 'liga':
        terms.append(f(X_train_encoded.columns.get_loc(col)))
    else:
        terms.append(s(X_train_encoded.columns.get_loc(col)))

gam_formula = sum(terms[1:], terms[0])

model_3 = LinearGAM(gam_formula).fit(X_train_encoded, y_train)


fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(18, 5))
XX_liga = model_3.generate_X_grid(term=0)
pdep_liga, conf_liga = model_3.partial_dependence(term=0, X=XX_liga, width=0.95)
ax0.plot(XX_liga[:, 0], pdep_liga, c="darkblue", lw=2)
ax0.plot(XX_liga[:, 0], conf_liga, c="crimson", linestyle="--", lw=1)
ax0.set_title("Partial Dependence of liga")
ax0.set_xlabel("Encoded League ID")
ax0.set_ylabel("Effect on Log Market Value")
XX_90s = model_3.generate_X_grid(term=1)
pdep_90s, conf_90s = model_3.partial_dependence(term=1, X=XX_90s, width=0.95)
ax1.plot(XX_90s[:, 1], pdep_90s, c="darkblue", lw=2)
ax1.plot(XX_90s[:, 1], conf_90s, c="crimson", linestyle="--", lw=1)
ax1.set_title("Partial Dependence of 90s")
ax1.set_xlabel("Raw 90s Played (0 to 38)")
XX_age = model_3.generate_X_grid(term=19)
pdep_age, conf_age = model_3.partial_dependence(term=19, X=XX_age, width=0.95)
ax2.plot(XX_age[:, 19], pdep_age, c="darkblue", lw=2)
ax2.plot(XX_age[:, 19], conf_age, c="crimson", linestyle="--", lw=1)
ax2.set_title("Partial Dependence of age")
ax2.set_xlabel("Raw Age in Years (17 to 35+)")
plt.tight_layout()
plt.show()



model3_pred = np.expm1( model_3.predict(X_test_encoded) )

model3_res = get_metrics(y_test, model3_pred)

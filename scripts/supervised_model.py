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
                #pl.col('equipo')
                #.str.to_lowercase()
                #.str.split(" ")
                #.list.get(0)
                #.alias('club_key')
                ]
            )
        .with_columns([
            pl.col('nombre').list.get(0).str.slice(0,1).alias("first"),
            pl.col('nombre').list.get(-1).alias("last_name")
            ])
        )
player_ids = (
        pl.scan_csv('data/raw/players.csv')
        .select(['player_id', 'name', 'date_of_birth', 'current_club_name', 'agent_name', 'country_of_citizenship'])
        .with_columns(
            [
                pl.col('name')
                .str.to_lowercase()
                .str.split(" "),
               # pl.col('current_club_name')
                #.str.to_lowercase()
                #.str.split(" ")
                #.list.get(0)
                #.alias("club_key")
                ]
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
data = final_plan.collect()

print(
    forwards_df.group_by("nombre")
    .len("count")
    .filter(pl.col("count") > 1)
    .sort("count", descending=True)
)


check = (pl.scan_csv('data/raw/player_valuations.csv')).collect()

players = pl.read_csv('data/raw/players.csv')

players = players.join(
        check,
        on = 'player_id',
        how = 'inner'
        )

data.filter(pl.col('current_club_name') == 'FC Barcelona').select('name')

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
    "name",
    "country_of_citizenship",
    "agent_name",
    "current_club_name",
    "market_value_in_eur",  
    "date",  
    "posicion",
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
)

data.write_parquet('data/raw/supervised_data.parquet')

data = data.to_pandas()

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

sns.boxplot(x = 'log_market_val', data = data, hue = 'posicion')
plt.show()

sns.relplot(x = 'goals_per_90', y = 'log_market_val', data = data)
plt.show()

### partimos los datos



#### Usamos una regresion simple linear para empezar

import statsmodels.formula.api as smf

features = [
    "C(liga)",
    "C(posicion)",
    "C(agent_name)",
    "C(posicion)",
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

from pygam import ExpectileGAM, LinearGAM, f, s
from sklearn.preprocessing import LabelEncoder


data = pd.read_parquet('data/raw/supervised_data.parquet')
data['log_market_val'] = np.log1p(data['market_value_in_eur'])
data.drop('temporada', axis = 1, inplace = True)
country_counts = data['country_of_citizenship'].value_counts()
frequent_countries = country_counts[country_counts > 30].index.tolist()
agent_counts = data['agent_name'].value_counts()
frequent_agents = agent_counts[agent_counts > 30].index.tolist()######
data['country_of_citizenship'] = data['country_of_citizenship'].where(
    data['country_of_citizenship'].isin(frequent_countries), 'Other'
)
data['agent_name'] = data['agent_name'].where(
    data['agent_name'].isin(frequent_agents), 'Other'
)
le_liga = LabelEncoder()
le_posicion = LabelEncoder()
le_country = LabelEncoder()
le_agent = LabelEncoder()
data["liga"] = le_liga.fit_transform(
    data["liga"].astype(str)
)
data["posicion"] = le_posicion.fit_transform(
    data["posicion"].astype(str)
)
data["country_of_citizenship"] = le_country.fit_transform(
    data["country_of_citizenship"].astype(str)
)
data["agent_name"] = le_agent.fit_transform(
    data["agent_name"].astype(str)
)
###############


data['Second Goal Assists'] = pd.to_numeric( data['Second Goal Assists'], errors = 'coerce' ).fillna(0)
data['Foul Won Penalty'] = pd.to_numeric( data['Foul Won Penalty'], errors = 'coerce' ).fillna(0)

data['current_club_name'] = data['current_club_name'].astype(str).str.strip()
raw_clubs = data["current_club_name"].unique().tolist()

high_value_keywords = [
    "Bayern Munich",
    "Arsenal FC",
    "Juventus FC",
    "Paris Saint-Germain",
    "Manchester City",
    "Chelsea FC",
    "Manchester United",
    "Liverpool FC",
    "Real Madrid",
    "Tottenham Hotspur",
    "Atlético de Madrid",
    "FC Barcelona",
    "AC Milan",
    "Inter Milan",
    "SSC Napoli",
    "Al-Nassr FC",
    "Al-Ahli SFC",
]
mid_tier_keywords = [
    "Atalanta BC",
    "RB Leipzig",
    "Stade Rennais FC",
    "Eintracht Frankfurt",
    "Sevilla FC",
    "Real Betis Balompié",
    "Real Sociedad",
    "Bologna FC 1909",
    "Olympique Lyon",
    "Villarreal CF",
    "Aston Villa",
    "Bayer 04 Leverkusen",
    "Nottingham Forest",
    "Wolverhampton Wanderers",
    "Valencia CF",
    "LOSC Lille",
    "Newcastle United",
    "Torino FC",
    "Girona FC",
    "Brighton & Hove Albion",
    "Ajax Amsterdam",
    "Athletic Bilbao",
    "AS Roma",
    "SS Lazio",
    "Genoa CFC",
    "Sporting CP",
    "SL Benfica",
    "FC Porto",
    "Borussia Mönchengladbach",
    "Everton FC",
    "Fulham FC",
    "Brentford FC",
    "Crystal Palace",
    "West Ham United",
    "VfB Stuttgart",
    "TSG 1899 Hoffenheim",
    "ACF Fiorentina",
    "VfL Wolfsburg",
    "Bournemouth",
    "Feyenoord Rotterdam",
    "Borussia Dortmund",
    "Nice",
    "Marseille",
    "Olympique Marseille",
    "RC Lens",
    "Stade Reims",
    "Montpellier HSC",
    "VfB Stuttgart",
    "Southampton FC",
    "Leeds United",
    "Leicester City",
]

club_tier_map = {}
for club in raw_clubs:
    if pd.isna(club):
        continue
    clean_name = str(club).strip()
    is_youth_or_reserve = any(
        kw in clean_name
        for kw in [
            "U21",
            "U23",
            "U19",
            "U18",
            " B",
            "Castilla",
            "Mestalla",
            "Fortuna",
            "Primavera",
            "Atlètic",
            "SAD",
            "II",
        ]
    )
    if is_youth_or_reserve or clean_name in ["Without Club"]:
        club_tier_map[club] = "low_tier"
    elif clean_name in high_value_keywords:  # <-- FIX: Exact match validation
        club_tier_map[club] = "high_tier"
    elif any(mt in clean_name for mt in mid_tier_keywords):
        club_tier_map[club] = "mid_tier"
    else:
        club_tier_map[club] = "low_tier"

data["club_bucket"] = data["current_club_name"].map(club_tier_map)

data['club_bucket'] = data.apply(lambda row: 'low_tier' if 'Atlètic' in str(row['current_club_name']) else ('high_tier' if 'Barcelona' in str(row['current_club_name']) else row['club_bucket']), axis=1)

print(
    data[data["current_club_name"] == "FC Barcelona"][
        ["name", "current_club_name", "club_bucket"]
    ]
)

le_club = LabelEncoder()
data['club_bucket']  = le_club.fit_transform(data['club_bucket'].astype(str))


inference = data[data['club_bucket'] == 'high_tier']

data.to_csv('data/raw/inference.csv', index = False)

from sklearn.model_selection import train_test_split

data = data.fillna(0)

train_data, test_data = train_test_split(
        data,
        test_size = 0.25,
        random_state = 69
        )

# Initialize a fresh isolated category encoder for the engineered groups

X_train_encoded = train_data.drop(['name', 'current_club_name', 'market_value_in_eur', 'log_market_val'], axis = 1)
y_train = train_data['log_market_val'].values
y_train_norm = train_data['market_value_in_eur'].values

X_test_encoded = test_data.drop(['name', 'current_club_name', 'market_value_in_eur', 'log_market_val'], axis = 1)
y_test = test_data['market_value_in_eur'].values

terms = []
for idx, col in enumerate(X_train_encoded.columns):
    if col in ["liga", "posicion", "country_of_citizenship", "agent_name", "club_bucket"]:
        terms.append(f(idx))  # Hard factor boundary
    else:
        terms.append(s(idx))  # Smooth spline curve




gam_formula = sum(terms[1:], terms[0])

model_3 = LinearGAM(gam_formula).fit(X_train_encoded, y_train)


fig, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4, figsize=(18, 5))
XX_liga = model_3.generate_X_grid(term=0)
pdep_liga, conf_liga = model_3.partial_dependence(term=0, X=XX_liga, width=0.95)
ax0.plot(XX_liga[:, 0], pdep_liga, c="darkblue", lw=2)
ax0.plot(XX_liga[:, 0], conf_liga, c="crimson", linestyle="--", lw=1)
ax0.set_title("Partial Dependence of POsition")
ax0.set_xlabel("Position Encoded")
ax0.set_ylabel("Effect on Log Market Value")
XX_90s = model_3.generate_X_grid(term=1)
pdep_90s, conf_90s = model_3.partial_dependence(term=1, X=XX_90s, width=0.95)
ax1.plot(XX_90s[:, 1], pdep_90s, c="darkblue", lw=2)
ax1.plot(XX_90s[:, 1], conf_90s, c="crimson", linestyle="--", lw=1)
ax1.set_title("Partial dependence of liga")
ax1.set_xlabel("Liga Encoded Value")
XX_age = model_3.generate_X_grid(term=22)
pdep_age, conf_age = model_3.partial_dependence(term=22, X=XX_age, width=0.95)
ax2.plot(XX_age[:, 22], pdep_age, c="darkblue", lw=2)
ax2.plot(XX_age[:, 22], conf_age, c="crimson", linestyle="--", lw=1)
ax2.set_title("Partial Dependence of age")
ax2.set_xlabel("Raw Age in Years (17 to 35+)")
XX_goals = model_3.generate_X_grid(term=3)
pdep_goals, conf_goals = model_3.partial_dependence(term=3, X=XX_goals, width=0.95)
ax3.plot(XX_goals[:, 3], pdep_goals, c="darkblue", lw=2)
ax3.plot(XX_goals[:, 3], conf_goals, c="crimson", linestyle="--", lw=1)
ax3.set_title("Partial Dependece of Goals per 90")
ax3.set_xlabel("Goals")
plt.tight_layout()
plt.show()



model3_pred = np.expm1( model_3.predict(X_test_encoded) )
model3_res = get_metrics(y_test_norm, model3_pred)


# usamos models de ensemblaje

import xgboost as xgb

xgb_model = xgb.XGBRegressor(
        n_estimators = 500,
        max_depth = 5,
        learning_rate = 0.05,
        subsample = 0.8,
        colsample_bytree = 0.8,
        random_state = 69
        )

xgb_model.fit(X_train_encoded, y_train)

### Checamos el insample accuracy


in_sample_pred = np.expm1(xgb_model.predict(X_train_encoded))
get_metrics(y_train_norm, in_sample_pred)


xgb_model.score(X_train_encoded, y_train)

importances = pd.Series(
        xgb_model.feature_importances_, index = X_train_encoded.columns
        ).sort_values(ascending = False)

# Checamos el out of sample

model4_pred = np.expm1(xgb_model.predict(X_test_encoded))
model4_res = get_metrics(model4_pred, y_test)


## hacemos un hyperparameter tuning 

xgb_base = xgb.XGBRegressor(random_state = 69)

param_grid = {
    "n_estimators": [300, 500, 700],
    "max_depth": [3, 4],  
    "learning_rate": [0.01, 0.03, 0.05],
    "min_child_weight": [3, 5, 7],  
    "gamma": [0, 0.1, 0.2],  
    "subsample": [0.7, 0.8],  
    "colsample_bytree": [0.7, 0.8],  
}

from sklearn.model_selection import RandomizedSearchCV

xgb_search = RandomizedSearchCV(
        estimator = xgb_base,
        param_distributions = param_grid,
        n_iter = 20,
        scoring = 'neg_mean_squared_error',
        cv = 5,
        verbose = 1,
        random_state = 69,
        n_jobs = -1
        )

xgb_search.fit(X_train_encoded, y_train)

model_5 = xgb_search.best_estimator_

model_5_is = np.expm1(model_5.predict(X_train_encoded))
get_metrics(y_train_norm, model_5_is)


model_5.score(X_train_encoded, y_train)

importances = pd.Series(
        xgb_model.feature_importances_, index = X_train_encoded.columns
        ).sort_values(ascending = False)

# Checamos el out of sample

model5_pred = np.expm1(model_5.predict(X_test_encoded))
model5_res = get_metrics(model5_pred, y_test)

model_5.save_model('models/xgboost.json')


### Usamos codigo para crear un Cross Validation
from sklearn.model_selection import KFold

def calculate_CV_metrics(actual, predicted):
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mape = np.mean(np.abs((actual - predicted) / y_true_euro)) * 100
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape}


kf = KFold(n_splits = 5, shuffle = True, random_state = 69)

cv_results = {"Linear Regression": [],  "GAM": [], "XGBoost": []}

for fold, (train_idx, val_idx) in enumerate(kf.split(train_data)):
    
    train_cv, val_cv = train_data.iloc[train_idx], train_data.iloc[val_idx]
    y_log, y_abs = train_data.loc[]

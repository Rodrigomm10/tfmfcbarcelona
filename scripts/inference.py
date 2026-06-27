import pandas as pd
import xgboost as xgb
import numpy as np


df = pd.read_csv('data/raw/inference.csv')

df['full_name'] = df['name'].str.strip("[]").str.replace("'", "").str.replace('"', '').str.title()

identifiers = ['full_name', 'current_club_name']

xgb_model = xgb.XGBRegressor()
xgb_model.load_model('models/xgboost.json')

features = xgb_model.get_booster().feature_names

inf_trial = df[features]

xgb_model.predict(inf_trial)

cols_to_keep = identifiers + features

clean_df = df[cols_to_keep]


clean_df.to_json("data/processed/inference.json", orient = 'records')

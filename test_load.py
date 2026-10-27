import app
import config
import pandas as pd
print('1')
app.matches_df = pd.read_csv(config.RESULTS_CSV, engine='python', encoding='utf-8')
print('2')
app.matches_df['date'] = pd.to_datetime(app.matches_df['date'])
print('3')
from model.fifa_ranking import load_rankings
app.rankings = load_rankings(config.FIFA_RANKINGS_CSV)
print('4')
app.goalscorers_df = pd.read_csv(config.GOALSCORERS_CSV, engine='python', encoding='utf-8')
print('5')
app.goalscorers_df['date'] = pd.to_datetime(app.goalscorers_df['date'])
print('6')

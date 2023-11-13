import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="Funny Hockey Stats",layout="wide")

st.title("Funny Hockey Stats")

goal_diff_tab, team_anal_tab, blow_calc_tab = st.tabs(['Goal Differentials','Team Analysis','Blowout Calculator'])


@st.cache_data
def load_df():
    df = pd.read_csv('game_scores.csv')
    df['goal_diff'] = (df['home_goals']-df['away_goals'])
    df['home_win'] = 1.0*(df['home_goals']>df['away_goals']) + 0.5*(df['home_goals']==df['away_goals'])
    return df

df_original = load_df()

@st.cache_data
def load_teams(df):
    return df["home_team"].unique().tolist()

@st.cache_data
def load_diffs(df: pd.DataFrame):
    return df["goal_diff"].unique()


# ***** GOAL DIFFERENTIAL TAB *****
st.sidebar.title("Filters")
teams = load_teams(df_original)
# diffs = load_diffs(df_original)\
filter_dict = {}
filter_dict['team'] = st.sidebar.selectbox("Select Team",teams,index=teams.index('Detroit Red Wings'))
min_diff,max_diff = st.sidebar.slider("Goal Differential",min_value=0, max_value=15,value=[0,15])
filter_dict['goal_diff'] = np.concatenate([np.arange(-max_diff,-min_diff+1,1),np.arange(min_diff,max_diff+1,1)])# + np.arange(-min_diff,-max_diff-1,-1)
filter_dict['start_date'] = str(st.sidebar.date_input('Start Date',datetime.datetime(2000,12,1)))
filter_dict['stop_date'] = str(st.sidebar.date_input('End Date','today'))

@st.cache_data
def load_filtered(filters: dict= filter_dict):
    filtered_df = df_original # Start with all the data

    # Date Filter
    start_date=filter_dict.get('start_date','2000-01-01')
    filtered_df = filtered_df[filtered_df['date']>start_date]
    
    # Goal Diff filter
    filtered_df = filtered_df[filtered_df['goal_diff'].isin(filter_dict.get('goal_diff',[]))]

    # Team filter
    if len(filter_dict.get('team',[]))>0:
        filtered_df = pd.concat([filtered_df[filtered_df['home_team']==(filter_dict.get('team',''))],filtered_df[filtered_df['away_team']==(filter_dict.get('team',''))]]).drop_duplicates()


    # for key, values in filters.items(): # iterate thru each filter key and remove stuff that doesnt match
    #     filtered_df = filtered_df[filtered_df[key].isin(values)]
        # filtered_df = pd.concat([filtered_df, selections]).drop_duplicates()

    # if len(filtered_df)==0: return df_original
    return filtered_df



diff_df = load_filtered(filter_dict)

diff_plot = px.scatter(diff_df,'date','goal_diff',color='home_win',color_discrete_sequence=['#FF5733', '#33FF77'])
goal_diff_tab.plotly_chart(diff_plot,use_container_width=True)

indx = np.arange(1, 10)
benford = pd.DataFrame([1,2,3,4,5,6,7,8,9])
for d in indx:
    benford.loc[d] = [np.log10(1 + (1.0 / d)) ]

filtered_home_wins = diff_df[diff_df['home_win'] == 1]
filtered_away_wins = diff_df[diff_df['home_win'] == 0]

diff_hist = px.histogram(diff_df,x="goal_diff",color="home_win")
goal_diff_tab.plotly_chart(diff_hist,use_container_width=True)


diff_hist2 = px.histogram(diff_df,y="goal_diff",color="home_win")
goal_diff_tab.plotly_chart(diff_hist2,use_container_width=True)

benf_hist = px.bar(benford)
goal_diff_tab.plotly_chart(benf_hist,use_container_width=True)

goal_diff_tab.dataframe(diff_df.sort_values("goal_diff",ascending=False))


fig = go.Figure()
fig.add_trace(go.Bar(
    y=[val*(val>0) for val in diff_df['goal_diff']],
    x=diff_df['date'],
    orientation='v',
    name='Home Win',
    marker_color='red',
    offset=0,
))
fig.add_trace(go.Bar(
    y=[val*(val<0) for val in diff_df['goal_diff']],
    x=diff_df['date'],
    orientation='v',
    name='Away Win',
    marker_color='blue',
    offset=0,
))
fig.update_layout(barmode='relative', title='Population Pyramid', yaxis_title='Age')
goal_diff_tab.plotly_chart(fig,use_container_width=True)

away_counts = filtered_away_wins["goal_diff"].value_counts()
home_counts = filtered_home_wins["goal_diff"].value_counts()

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=home_counts.index,
    x=home_counts.values,
    orientation='h',
    name='Home Win',
    marker_color='red',
))
fig2.add_trace(go.Bar(
    y=away_counts.index*-1,
    x=away_counts.values*-1,
    orientation='h',
    name='Away Win',
    marker_color='blue',
))
# fig2.update_xaxes(type='log')
fig2.update_layout(barmode='relative', title='Population Pyramid', yaxis_title='Age')
goal_diff_tab.plotly_chart(fig2,use_container_width=True)

# if __name__ == "__main__":
#     filter_dict['home_team'] = ['Detroit Red Wings','Pittsburgh Penguins']
#     print(load_filtered(diff_df_original,filter_dict))


pivot_table = diff_df.pivot_table(index='away_goals', columns='home_goals', aggfunc='size', fill_value=0)
x = pivot_table.columns
y = pivot_table.index
z = pivot_table.values
hm = go.Figure(data=go.Heatmap(x=x, y=y, z=z, colorscale='Viridis',))
hm.update_layout(scene=dict(xaxis_title='Away Goals', yaxis_title='Home Goals', zaxis_title='Occurrences'),
                  title='3D Heatmap of Score Space')
goal_diff_tab.plotly_chart(hm)

# Group by both columns and count occurrences
grouped = diff_df.groupby(['away_goals', 'home_goals']).size().reset_index(name='Count')
d3 = go.Figure(data=[go.Mesh3d(
    x=grouped['away_goals'],
    y=grouped['home_goals'],
    z=grouped['Count'],
    # color=grouped['Count'],
    colorscale='Viridis',
    # colorbar_title='Count',
    intensity=grouped['Count'],
    showscale=True,
    # marker=dict(size=12, color=grouped['Count'], colorscale='Viridis', colorbar=dict(title='Count'))
)])
d3.update_layout(scene=dict(xaxis_title='Away Goals', yaxis_title='Home Goals', zaxis_title='Count'),
                  title='3D Scatter Plot of DataFrame Columns')
goal_diff_tab.plotly_chart(d3)


# ***** TEAM ANALYSIS TAB *****
# Biggest wins
# Biggest losses
# Average goal diff by team

@st.cache_data
def load_wins(filters: dict= filter_dict):
    filtered_df = diff_df # Start with all the data
    
    # Goal Diff filter
    filtered_df = filtered_df[filtered_df['goal_diff'].isin(filter_dict.get('goal_diff',[]))]

    # Team filter
    if len(filter_dict.get('team',[]))>0:
        home_games = filtered_df[filtered_df['home_team']==(filter_dict.get('team',''))]
        home_games['opponent']=home_games['away_team']
        home_games['win']=home_games['goal_diff']>0
        home_games['win']=home_games['goal_diff']>0
        away_games = filtered_df[filtered_df['home_team']==(filter_dict.get('team',''))]
        away_games['opponent']=away_games['home_team']
        home_games['win']=home_games['goal_diff']<0
        away_games['goal_diff']=-1*away_games['goal_diff']
        all_games = pd.concat([home_games,away_games])

        return all_games


    # for key, values in filters.items(): # iterate thru each filter key and remove stuff that doesnt match
    #     filtered_df = filtered_df[filtered_df[key].isin(values)]
        # filtered_df = pd.concat([filtered_df, selections]).drop_duplicates()

    # if len(filtered_df)==0: return df_original
    return filtered_df

team_games = load_wins(filter_dict)

opponent_data = team_games.groupby(['opponent'])
team_anal_tab.header('Average Goal Differential by Opponent')
diff_bar = px.bar(opponent_data['goal_diff'].mean().sort_values(ascending=False))
avgd_1, avgd_2 = team_anal_tab.columns([6,1])
avgd_1.plotly_chart(diff_bar,use_container_width=True)
# avgd_2.metric('Average Goal Differential',team_games['goal_diff'])
x=team_games['goal_diff']
print(x.values)
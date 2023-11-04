import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Funny Hockey Stats")

st.title("Funny Hockey Stats")

@st.cache_data
def load_df():
    return pd.read_csv('game_scores.csv')

df = load_df()
df['goal_diff'] = (df['home_goals']-df['away_goals'])
df['home_win'] = df['home_goals']>df['away_goals']

st.button("Refresh",on_click=load_df)
diff_plot = px.scatter(df,'date','goal_diff',color='home_win',color_discrete_sequence=['#FF5733', '#33FF77'])
st.plotly_chart(diff_plot)

indx = np.arange(1, 10)
benford = pd.DataFrame([1,2,3,4,5,6,7,8,9])
for d in indx:
    benford.loc[d] = [np.log10(1 + (1.0 / d)) ]

diff_hist = px.histogram(df,x="goal_diff",color="home_win")
st.plotly_chart(diff_hist)
diff_hist2 = px.histogram(df,y="goal_diff",color="home_win")
st.plotly_chart(diff_hist2)

benf_hist = px.bar(benford)
st.plotly_chart(benf_hist)

st.dataframe(df.sort_values("goal_diff",ascending=False))

filtered_home_wins = df[df['home_win'] == 1]
filtered_away_wins = df[df['home_win'] == 0]

fig = go.Figure()
fig.add_trace(go.Bar(
    y=[val*(val>0) for val in df['goal_diff']],
    x=df['date'],
    orientation='v',
    name='Home Win',
    marker_color='red',
    offset=0,
))
fig.add_trace(go.Bar(
    y=[val*(val<0) for val in df['goal_diff']],
    x=df['date'],
    orientation='v',
    name='Away Win',
    marker_color='blue',
    offset=0,
))
fig.update_layout(barmode='relative', title='Population Pyramid', yaxis_title='Age')
st.plotly_chart(fig)

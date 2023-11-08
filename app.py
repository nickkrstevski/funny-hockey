import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Funny Hockey Stats",layout="wide")

st.title("Funny Hockey Stats")


@st.cache_data
def load_df():
    df = pd.read_csv('game_scores.csv')
    df['goal_diff'] = (df['home_goals']-df['away_goals'])
    df['home_win'] = 1.0*(df['home_goals']>df['away_goals']) + 0.5*(df['home_goals']==df['away_goals'])
    return df

df_original = load_df()

@st.cache_data
def load_teams(df):
    return df["home_team"].unique()

@st.cache_data
def load_diffs(df: pd.DataFrame):
    return df["goal_diff"].unique()


st.sidebar.title("Filters")
teams = load_teams(df_original)
# diffs = load_diffs(df_original)
filter_dict = {}
filter_dict['home_team'] = st.sidebar.multiselect("Team",teams)
filter_dict['away_team'] = filter_dict['home_team']
min_diff,max_diff = st.sidebar.slider("Goal Differential",min_value=1, max_value=10,value=[1,10])
filter_dict['goal_diff'] = np.arange(min_diff,max_diff+1,1)# + np.arange(-min_diff,-max_diff-1,-1)
st.sidebar.text(filter_dict['goal_diff'])
@st.cache_data
def load_filtered(filters: dict= filter_dict):
    filtered_df =   
    for key, values in filters.items():
        selections = df_original[df_original[key].isin(values)]
        filtered_df = pd.concat([filtered_df, selections]).drop_duplicates()

    if len(filtered_df)==0: return df_original
    else: return filtered_df



df = load_filtered(filter_dict)

st.button("Refresh",on_click=load_filtered)
diff_plot = px.scatter(df,'date','goal_diff',color='home_win',color_discrete_sequence=['#FF5733', '#33FF77'])
st.plotly_chart(diff_plot,use_container_width=True)

indx = np.arange(1, 10)
benford = pd.DataFrame([1,2,3,4,5,6,7,8,9])
for d in indx:
    benford.loc[d] = [np.log10(1 + (1.0 / d)) ]

filtered_home_wins = df[df['home_win'] == 1]
filtered_away_wins = df[df['home_win'] == 0]

diff_hist = px.histogram(df,x="goal_diff",color="home_win")
st.plotly_chart(diff_hist,use_container_width=True)


diff_hist2 = px.histogram(df,y="goal_diff",color="home_win")
st.plotly_chart(diff_hist2,use_container_width=True)

benf_hist = px.bar(benford)
st.plotly_chart(benf_hist,use_container_width=True)

st.dataframe(df.sort_values("goal_diff",ascending=False))


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
st.plotly_chart(fig,use_container_width=True)

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
st.plotly_chart(fig2,use_container_width=True)

# if __name__ == "__main__":
#     filter_dict['home_team'] = ['Detroit Red Wings','Pittsburgh Penguins']
#     print(load_filtered(df_original,filter_dict))


pivot_table = df.pivot_table(index='away_goals', columns='home_goals', aggfunc='size', fill_value=0)
x = pivot_table.columns
y = pivot_table.index
z = pivot_table.values
hm = go.Figure(data=go.Heatmap(x=x, y=y, z=z, colorscale='Viridis'))
hm.update_layout(scene=dict(xaxis_title='Away Goals', yaxis_title='Home Goals', zaxis_title='Occurrences'),
                  title='3D Heatmap of Score Space')
st.plotly_chart(hm)

# Group by both columns and count occurrences
grouped = df.groupby(['away_goals', 'home_goals']).size().reset_index(name='Count')
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
st.plotly_chart(d3)
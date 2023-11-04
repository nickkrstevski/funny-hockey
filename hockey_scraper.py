import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import os
import time
import numpy as np

data_fp = "game_scores.csv"
column_headers = ['away_team','away_goals','home_team','home_goals','date']

def update_csv(df: pd.DataFrame):
    with open(data_fp, 'w') as file:
        file.truncate(0) #NUKE IT        
    print("printing")
    df.to_csv(data_fp,index=False)

try:
    old_bigdata = pd.read_csv(data_fp)
except:
    if input("No previous data found, wish to proceed? (y/n)").lower() == 'y':
        old_bigdata = pd.DataFrame(columns = column_headers)
        update_csv(old_bigdata)
    else: exit()

bigdata = pd.DataFrame(columns = column_headers)

searched_list = old_bigdata["date"]

start_date = datetime(2010, 1, 1)
# start_date = datetime(2023, 10, 1)
end_date = datetime(2023, 11, 3)

timerange = start_date-end_date
already_searched = 0

with tqdm(range(0, timerange.days),total=timerange.days,unit='days') as pbar:
    search_date = start_date
    while search_date <= end_date:
        if searched_list.str.contains(search_date.strftime('%Y-%m-%d')).any():
            search_date += timedelta(days=1) # INCREMENT DAY
            pbar.update(1)
            already_searched+=1
            continue
        dfs = [] # CLEAR DFs
        day = search_date.day
        month = search_date.month
        year = search_date.year
        url = f"https://www.hockey-reference.com/boxscores/index.fcgi?month={month}&day={day}&year={year}"
        try:
            response = requests.get(url, timeout=1)
            soup = BeautifulSoup(response.content, 'html.parser')
            div_elements = soup.find_all('div', class_='game_summary')
            number_of_elements = len(div_elements)
            if number_of_elements==0:
                search_date += timedelta(days=1) # INCREMENT DAY
                pbar.update(1)
                bigdata.loc[len(bigdata)] = ['','','','',search_date.strftime('%Y-%m-%d')]
                continue
            dfs = pd.read_html(response.content,attrs={'class':'teams'})
        except Exception as e:
            # print(f"Failed {search_date}: {e}")
            bigdata.loc[len(bigdata)] = ['','','','',search_date.strftime('%Y-%m-%d')]
        for df in dfs:
            if len(df) == 2: # Single game stat
                away_team = df.iloc[0,0]
                away_score = df.iloc[0,1]
                home_team = df.iloc[1,0]
                home_score = df.iloc[1,1]
                bigdata.loc[len(bigdata)] = [away_team,away_score,home_team,home_score,search_date.strftime('%Y-%m-%d')]
        
        search_date += timedelta(days=1) # INCREMENT DAY
        pbar.update(1)        

merged_df = pd.concat([old_bigdata, bigdata]).drop_duplicates()
added = len(merged_df)-len(old_bigdata)
duplicates = len(old_bigdata)+len(bigdata)-len(merged_df)

print(f"Added: {added} and skipped {duplicates} duplicates, already searched {already_searched}")

update_csv(merged_df)


import requests
import pandas as pd
from bs4 import BeautifulSoup

print("running")
url = "https://www.hockey-reference.com/boxscores/?year=2000&month=1&day=1"
response = requests.get(url, timeout=2)
print("gotit")

soup = BeautifulSoup(response.content, 'html.parser')
div_elements = soup.find_all('div', class_='game_summary')
number_of_elements = len(div_elements)

print(response.content)

print(number_of_elements)
# dfs = pd.read_html(response.content,attrs={"class":"teams"})
# print(dfs)
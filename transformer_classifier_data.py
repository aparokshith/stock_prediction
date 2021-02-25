# -*- coding: utf-8 -*-

import pandas as pd
#%%
import json
import pickle
from tqdm import tqdm
import pandas_market_calendars as mcal
from nltk.stem import PorterStemmer 
from nltk.corpus import stopwords
import re
import unidecode
ps = PorterStemmer()
cachedStopWords = stopwords.words('english')
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date='2017-07-01', end_date='2020-02-14')
#%%
def get_direc(row):
    if row['open'] >= row['close']:
        return -1
    else:
        return 1
#%%
def get_date_time(row):
    date = row['date']
    date = date.replace('.','-')
    return date + " " + row['time']

#%%
def cleaner(tes):
    # REPLACE_NO_SPACE = re.compile("[$;:!-\'?,\"()\[\]]")
    # REPLACE_U_NAME = re.compile("@[\S]+")
    # REPLACE_DIGITS = re.compile("\d")
    # REPLACE_W_SPACE = re.compile("_")
    # tes = re.sub(REPLACE_NO_SPACE, '',tes)
    # tes = re.sub(REPLACE_U_NAME,'',tes)
    # tes = re.sub(REPLACE_DIGITS,'',tes)
    # tes = re.sub(REPLACE_W_SPACE,'',tes)
    tes = re.sub('[^a-zA-Z.]+', ' ', tes)
    tes = tes.lower()
    return tes
#%%
def stop_removal(lists):
    text = ' '.join([ps.stem(word) for word in lists.split() if word not in cachedStopWords])
    return text
#%%
colnames = ['date','time','open','high','low','close','volume']
df_chart = pd.read_csv("F:/SWM_project/CHARTS/AMAZON60.csv", names=colnames)
df_chart['direction'] = df_chart.apply(lambda row: get_direc(row), axis = 1)
df_chart['date_time'] = df_chart.apply(lambda row: get_date_time(row), axis = 1)
#%%
with open('F:/SWM_project/meta_files/news_topics_usingJSON.pickle', 'rb') as handle:
    ticker_news = pickle.load(handle)
    
with open('F:/SWM_project/meta_files/trading_news.pickle', 'rb') as handle:
    trading_news = pickle.load(handle)
#%%
news_dict = {}
for key in tqdm(trading_news):
    for file in trading_news[key]:
        if file in ticker_news['AMZN']:
            news_dict.setdefault(file, key)
#%%
date_direction_dict = {}
for idx, rows in tqdm(df_chart.iterrows(), total=df_chart.shape[0]):
    if nyse.open_at_time(early, pd.Timestamp(rows['date_time'], tz='America/New_York')):
        date_direction_dict.setdefault(rows['date_time'] + ':00', rows['direction'])
        
#%%

text_list = []
for path in tqdm(news_dict):
    with open(path,encoding='utf-8' ) as json_file:
            data = json.load(json_file)
            
    text = unidecode.unidecode(data['text'])
    sentences_list = stop_removal(cleaner(text))
    if news_dict[path] in date_direction_dict:
        direc = date_direction_dict[news_dict[path]]
    else:
        continue
    
    text_list.append([sentences_list, direc])
        
#%%
df_data = pd.DataFrame(text_list, columns = ["news", "direction"])
df_data.to_csv('F:/SWM_project/meta_files/news_direction.csv',index = False)
        

        
        
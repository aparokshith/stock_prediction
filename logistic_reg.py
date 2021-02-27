# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 18:48:07 2021
"""
# =============================================================================
# 1. Combine the charts data and the n-gram features
# 2. Select top 1000 features
# 3. use the combined data to run sparse logistic regression
# 4. fin-tune and report top features that drive the stock 
# =============================================================================

import pandas as pd
#%%
import json
import os
import pickle
from tqdm import tqdm
import pandas_market_calendars as mcal
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date='2017-07-01', end_date='2020-02-14')
n_gms = 2
#%%
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_selection import SelectKBest 
from sklearn.feature_selection import chi2 
from sklearn import model_selection
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
colnames = ['date','time','open','high','low','close','volume']
df_chart = pd.read_csv("F:/SWM_project/CHARTS/AMAZON60.csv", names=colnames)
df_chart['direction'] = df_chart.apply(lambda row: get_direc(row), axis = 1)
df_chart['date_time'] = df_chart.apply(lambda row: get_date_time(row), axis = 1)

with open('F:/SWM_project/meta_files/news_topics_usingJSON.pickle', 'rb') as handle:
    ticker_news = pickle.load(handle)
    
with open('F:/SWM_project/meta_files/trading_news.pickle', 'rb') as handle:
    trading_news = pickle.load(handle)
    
news_dict = {}
for key in tqdm(trading_news):
    for file in trading_news[key]:
        if file in ticker_news['AMZN']:
            news_dict.setdefault(file, key)

date_direction_dict = {}
for idx, rows in tqdm(df_chart.iterrows(), total=df_chart.shape[0]):
    if nyse.open_at_time(early, pd.Timestamp(rows['date_time'], tz='America/New_York')):
        date_direction_dict.setdefault(rows['date_time'] + ':00', rows['direction'])
#%%
with open('F:/SWM_project/meta_files/all_grams' + str(n_gms) +'(column_names).pickle', 'rb') as handle:
    all_grams = pickle.load(handle)
    
with open('F:/SWM_project/meta_files/news' + str(n_gms) +'(row_index).pickle', 'rb') as handle:
    news = pickle.load(handle)
    
with open('F:/SWM_project/meta_files/all_occurance' + str(n_gms) +'(features).pickle', 'rb') as handle:
    all_occurance = pickle.load(handle)
#%%

labels = []
features = []
for idx, path in enumerate(news):
    if news_dict[path] in date_direction_dict:
        direc = date_direction_dict[news_dict[path]]
        labels.append(direc)
        features.append(all_occurance[idx])
    else:
        continue
#%%
#reshape csr to 1Darray
features_array = []
for csr in tqdm(features):
    # print(type(csr))
    arr = csr.todense()
    raveled = np.asarray(arr).ravel()
    features_array.append(raveled)

#%%
chi2_features = SelectKBest(chi2, k = 1000) 
X_kbest_features = chi2_features.fit_transform(features_array, labels)
#%%
#Verify op shape
#print(X_kbest_features.shape)

mask = chi2_features.get_support()
new_features = []
for bool, feature in zip(mask, all_grams):
    if bool:
        new_features.append(feature)
print("Features reduced from {} to {}".format(len(all_grams),len(new_features)))

#%%
'''
    Stratified Test-Train split
'''
X_train, X_test, y_train, y_test = train_test_split(X_kbest_features, labels,
                                                    stratify=labels,
                                                    test_size=0.20)
#%%
kfold = model_selection.KFold(n_splits=10, random_state=7,shuffle=(True))
model = LogisticRegression(penalty = 'l1', C = 10,tol = 0.001 , solver = 'saga', random_state=42,max_iter = 1500)
results = model_selection.cross_val_score(model, X_kbest_features, labels, cv=kfold)
print("Accuracy: %.3f%% (%.3f%%)" % (results.mean()*100.0, results.std()*100.0))

#%%
clf = LogisticRegression(penalty = 'l1', C = 10,tol = 0.001 , solver = 'saga', random_state=42,max_iter = 1500)
clf.fit(X_train,y_train)
print(clf.score(X_test, y_test))
predicted = clf.predict(X_test)
print(classification_report(y_test, predicted))
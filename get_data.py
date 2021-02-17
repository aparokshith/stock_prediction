# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:06:40 2021

@author: aparo
"""
# =============================================================================
# This module does the following
# 1. converts the time-zone given in NEWS articles and charts data to nearest trading time
# 2. groups 1hr news data to the next trading hour
# =============================================================================

#%%
from datetime import time, datetime, timedelta
import pandas as pd
import json
import os
import pickle
from tqdm import tqdm
import pandas_market_calendars as mcal
nyse = mcal.get_calendar('NYSE')
#%%
early = nyse.schedule(start_date='2017-07-01', end_date='2020-02-14')

#%%
def add_one_hours(the_time):
    # the_time = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S.000%z')
    new_time = the_time + timedelta(hours=1)
    return new_time

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

#%%
def get_trading_hour(path):
    with open(path,encoding='utf-8' ) as json_file:
        data = json.load(json_file)
    
    # print(data['published'])'
    if 'published' in data.keys():
        
        orig_dt = datetime.strptime(data['published'], '%Y-%m-%dT%H:%M:%S.000%z')
        utc_time_value = orig_dt - orig_dt.utcoffset()
        utc_dt = utc_time_value.replace(tzinfo=None)
        utc_dt = hour_rounder(utc_dt)
        if nyse.open_at_time(early, pd.Timestamp(str(utc_dt), tz = 'utc')):
            return utc_dt
        else:
            
            while nyse.open_at_time(early, pd.Timestamp(str(utc_dt), tz = 'utc')) != True:
                utc_dt = add_one_hours(utc_dt)
            return utc_dt
    else:
        return -1
    

#%%
hours_files = {}
subdirs = [x[0] for x in os.walk('F:/SWM_project/News')]                                                                            
for subdir in tqdm(subdirs):                                                                                            
    files = os.walk(subdir).__next__()[2]                                                                             
    if (len(files) > 0):                                                                                          
        for file in files:
            path = os.path.join(subdir, file)
            trade_hour = get_trading_hour(path)
            if trade_hour == -1:
                continue
            else:
                hours_files.setdefault(str(trade_hour), [])
                hours_files[str(trade_hour)].append(str(path))
                            

#%%
with open('F:/SWM_project/meta_files/trading_news.pickle', 'wb') as handle:
    pickle.dump(hours_files, handle, protocol=pickle.HIGHEST_PROTOCOL)

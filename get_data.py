# -*- coding: utf-8 -*-

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
df_intervals = pd.date_range("13:30", "21:30", freq="60min").time # change frequency according to the data
#%%
def add_hours(the_time, hours_to_add): 
    # the_time = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S.000%z')
    new_time = the_time + timedelta(hours=hours_to_add)
    return new_time

# def hour_rounder(t):
#     # Rounds to nearest hour by adding a timedelta hour if minute >= 30
#     return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
#                +timedelta(hours=t.minute//30))

def hour_rounder(dt):
    return dt + (datetime.min - dt) % timedelta(minutes=30)
#%%
# with open('F:/SWM_project/news_0000006.json',encoding='utf-8') as json_file:
#     data = json.load(json_file)

# #%%
# orig_dt = datetime.strptime('2018-01-03T15:30:00.000+00:00', '%Y-%m-%dT%H:%M:%S.000%z')
# utc_time_value = orig_dt - orig_dt.utcoffset()
# utc_dt = utc_time_value.replace(tzinfo=None)
# stock_time = add_hours(utc_dt,1.01)
# stock_date = stock_time.date()
# trade_time = min(df_intervals, key=lambda d: abs(datetime.combine(stock_date, d) - stock_time))
# print(datetime.combine(stock_date, trade_time))
# #%%
# print(stock_time.replace(minute = 30))
# #%%
# utc_dt_round = hour_rounder(utc_dt)
# if '30' in str(utc_dt_round.minute):
#     print(add_one_hours(utc_dt_round))
#%%
def get_trading_hour(path):
    with open(path,encoding='utf-8' ) as json_file:
        data = json.load(json_file)
    
    # print(data['published'])'
    if 'published' in data.keys():
        
        orig_dt = datetime.strptime(data['published'], '%Y-%m-%dT%H:%M:%S.000%z')
        utc_time_value = orig_dt - orig_dt.utcoffset()
        utc_dt = utc_time_value.replace(tzinfo=None)
        stock_time = add_hours(utc_dt,1.01)
        stock_date = stock_time.date()
        trade_time = min(df_intervals, key=lambda d: abs(datetime.combine(stock_date, d) - stock_time))
        # utc_dt = hour_rounder(utc_dt)
        utc_dt = datetime.combine(stock_date, trade_time)
        if nyse.open_at_time(early, pd.Timestamp(str(utc_dt), tz = 'utc')):
            return utc_dt
        else:
            
            while nyse.open_at_time(early, pd.Timestamp(str(utc_dt), tz = 'utc')) != True:
                utc_dt = add_hours(utc_dt,0.5)
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
with open('F:/SWM_project/meta_files/trading_news_fixed.pickle', 'wb') as handle:
    pickle.dump(hours_files, handle, protocol=pickle.HIGHEST_PROTOCOL)

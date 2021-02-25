# -*- coding: utf-8 -*-

import os
from tqdm import tqdm
import pickle
import json
from tqdm import tqdm
#%%

def get_news_topic(path):
    apple = False
    amazon = False
    with open(path,encoding='utf-8' ) as json_file:
            data = json.load(json_file)
            
    for item in data['entities']['organizations']:
        if ('aapl' in item['name']) or ('apple' in item['name']):
            apple = True
        if ('amzn' in item['name']) or ('amazon' in item['name']):
            amazon = True
    return apple, amazon


#%%
news_topics = {}
subdirs = [x[0] for x in os.walk('F:/SWM_project/News')]                                                                            
for subdir in tqdm(subdirs):                                                                                            
    files = os.walk(subdir).__next__()[2]                                                                             
    if (len(files) > 0):                                                                                          
        for file in files:
            path = os.path.join(subdir, file)
            apple, amazon = get_news_topic(path)
            if (not apple) and (not amazon):
                continue
            if apple:
                
                news_topics.setdefault('AAPL', [])
                news_topics['AAPL'].append(str(path))
                
            if amazon:
                news_topics.setdefault('AMZN', [])
                news_topics['AMZN'].append(str(path))
                
#%%
with open('F:/SWM_project/meta_files/news_topics_usingJSON.pickle', 'wb') as handle:
    pickle.dump(news_topics, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    
# -*- coding: utf-8 -*-


import pandas as pd
import pickle
import nltk
import re
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import json
import unidecode
import os
from tqdm import tqdm
from langdetect import detect
#%%
cachedStopWords = stopwords.words('english')
#%%
def cleaner(tes):
    REPLACE_NO_SPACE = re.compile("[$;:!-\'?,\"()\[\]]")
    REPLACE_U_NAME = re.compile("@[\S]+")
    REPLACE_DIGITS = re.compile("\d")
    REPLACE_W_SPACE = re.compile("_")
    tes = re.sub(REPLACE_NO_SPACE, '',tes)
    tes = re.sub(REPLACE_U_NAME,'',tes)
    tes = re.sub(REPLACE_DIGITS,'',tes)
    tes = re.sub(REPLACE_W_SPACE,'',tes)
    tes = tes.lower()
    return tes
#%%
def stop_removal(lists):
    text = ' '.join([word for word in lists.split() if word not in cachedStopWords])
    return text

#%%
def print_top_words(model, feature_names, n_top_words):
    messages = []
    for index, topic in enumerate(model.components_):
        message = " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1 :-1]])
        messages.append(message)
    return messages
#%%
def overlap_finder(topic):
    overlap_topics = []
    for i in range(len(topic)-1):
        check = topic[i].split()
        for lis in topic[i+1:]:            
            overlap_topics.append(list(set(check) & set(lis.split())))
    return overlap_topics

#%%
exceps = []
def get_news_topic(path):
    global exceps
    apple = False
    amazon = False
    with open(path,encoding='utf-8' ) as json_file:
            data = json.load(json_file)
    text = unidecode.unidecode(data['text'])
    lang = detect(text)
    
    if lang != 'en': # ignore non-english NEWS articles
        return apple, amazon
    
    sentences_list = stop_removal(cleaner(text)).split('.')
    
    if len(sentences_list)  == 0:
        exceps.append(path)
        return apple, amazon
    try:
        
        cv = CountVectorizer(binary=True)
        cv.fit(sentences_list)
        count_vec = cv.fit_transform(sentences_list)
        lda = LatentDirichletAllocation(n_components=5, max_iter=5,topic_word_prior = 0.1,
                                    learning_method = 'online',
                                    learning_offset = 50.,
                                    random_state = 0)
        lda.fit(count_vec)
        n_top_words = 40
        tf_feature_names = cv.get_feature_names()
        topics = print_top_words(lda, tf_feature_names, n_top_words)
        overlap_found = overlap_finder(topics)
        
        
        for topic in overlap_found:
            if ('aapl' in topic) or ('apple' in topic):
                apple = True
            if ('amzn' in topic) or ('amazon' in topic):
                amazon = True
        return apple, amazon
    except:
        exceps.append(path)
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
with open('F:/SWM_project/meta_files/news_topics.pickle', 'wb') as handle:
    pickle.dump(news_topics, handle, protocol=pickle.HIGHEST_PROTOCOL)

    

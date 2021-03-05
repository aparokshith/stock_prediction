# -*- coding: utf-8 -*-

import nltk
from nltk.util import ngrams
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import pickle
import unidecode
from scipy.sparse import csr_matrix
import re
from tqdm import tqdm
import pandas as pd
ps = PorterStemmer()
cachedStopWords = stopwords.words('english')
#%%

# Function to generate n-grams from sentences.
def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]


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
# with open('F:/SWM_project/news_0000006.json',encoding='utf-8' ) as json_file:
#             data = json.load(json_file)

# text = unidecode.unidecode(data['text'])
# sentences_list = stop_removal(cleaner(text)).split('.')

# #%%
# doc_bi_gram = set()
# for sent in sentences_list:
#     bi_gram = extract_ngrams(sent, 2)
#     doc_bi_gram = doc_bi_gram.union(set(bi_gram))
    
    
#%%
with open('F:/SWM_project/meta_files/news_topics_usingJSON.pickle', 'rb') as handle:
    ticker_news = pickle.load(handle)
#%%
n_gms = 3 # Change here for n-gram
news_grams = {}
for news in tqdm(ticker_news['AMZN']):
    
    with open(news,encoding='utf-8' ) as json_file:
            data = json.load(json_file)
            
    text = unidecode.unidecode(data['text'])
    sentences_list = stop_removal(cleaner(text)).split('.')
    doc_gram = set()
    for sent in sentences_list:
        gram = extract_ngrams(sent,n_gms) 
        doc_gram = doc_gram.union(set(gram))
    
    news_grams.setdefault(news,doc_gram)
    
#%%
print("combining grams into set")
all_grams = set()
for item in tqdm(news_grams):
    all_grams = all_grams.union(news_grams[item])
    
#%%

all_grams = list(all_grams)
news = list(news_grams.keys())

all_occurance = []
for item in tqdm(news):
    doc_occurance = []
    for gram in all_grams:
        if gram in news_grams[item]:
            doc_occurance.append(1)
        else:
            doc_occurance.append(0)
    # doc_occurance.insert(0,item)
    all_occurance.append(csr_matrix(doc_occurance)) # generates a list of CSR arrays
        
#%%
def save_pickle(file, path):
    with open(path, 'wb') as handle:
        pickle.dump(file, handle, protocol=pickle.HIGHEST_PROTOCOL)
#%%
save_pickle(all_grams, 'F:/SWM_project/meta_files/all_grams' + str(n_gms) +'(column_names).pickle')
save_pickle(news, 'F:/SWM_project/meta_files/news' + str(n_gms) +'(row_index).pickle')
save_pickle(all_occurance, 'F:/SWM_project/meta_files/all_occurance' + str(n_gms) +'(features).pickle')
    
#%%
# all_occurance.insert(0, all_grams)
import csv
fo = open("F:/SWM_project/meta_files/" + n_gms +"_grams_features_new.csv", "a")

w = csv.writer(fo, delimiter = ',')
for row in tqdm(all_occurance):
    w.writerow(row.toarray().ravel())
fo.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
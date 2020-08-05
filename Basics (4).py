#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

jeopardy = pd.read_csv('jeopardy.csv')
jeopardy.columns = jeopardy.columns.str.replace(' ', '')


# In[2]:


import re

def normalize_text(a_string):
    a_string = a_string.lower()
    a_string = re.sub('[^A-Za-z0-9\s]', '', a_string)
    a_string = re.sub('\s+', ' ', a_string)
    return a_string

jeopardy['clean_question'] = jeopardy['Question'].apply(normalize_text)
jeopardy['clean_answer'] = jeopardy['Answer'].apply(normalize_text)


# In[3]:


def normalize_value(value):
    value = re.sub("[^A-Za-z0-9\s]", "", value)
    try:
        value = int(value)
    except Exception:
        value = 0
    return value

jeopardy['clean_value'] = jeopardy['Value'].apply(normalize_value)
jeopardy['AirDate'] = pd.to_datetime(jeopardy['AirDate'])


# In[4]:


def repeats(row):
    split_answer = row['clean_answer'].split()
    split_question = row['clean_question'].split()
    
    match_count = 0
    if 'the' in split_answer:
        split_answer.remove('the')
    if len(split_answer) == 0:
        return 0
    
    for answer in split_answer:
        if answer in split_question:
            match_count += 1
   
    result = match_count / len(split_answer)
    return result

jeopardy['answer_in_question'] = jeopardy.apply(repeats, axis = 1)
answer_in_question_mean = jeopardy['answer_in_question'].mean()


# In[5]:


question_overlap = []
terms_used = set()

jeopardy = jeopardy.sort_values('AirDate')

for index, row in jeopardy.iterrows():
    split_question = row['clean_question'].split(' ')
    split_question = [c for c in split_question if len(c) > 5]
    match_count = 0
    
    for word in split_question:
        if word in terms_used:
            match_count += 1
    for word in split_question:
        terms_used.add(word)
    if len(split_question) > 0:
        match_count /= len(split_question)
    question_overlap.append(match_count)
    
jeopardy['question_overlap'] = question_overlap
qo_mean = jeopardy['question_overlap'].mean()
print(qo_mean)


# In[6]:


def value(row):
    value = 0
    if row['clean_value'] > 800:
        value = 1
    else:
        value = 0
    return value

jeopardy['high_value'] = jeopardy.apply(value, axis = 1)


# In[7]:


def count_value(word):
    low_count = 0
    high_count = 0
    
    for index, row in jeopardy.iterrows():
        if term in row['clean_question'].split(' '):
            if row['high_value'] == 1:
                high_count += 1
            else:
                low_count += 1
    return high_count, low_count


# In[9]:


from random import choice

terms_used_list = list(terms_used)
comparison_terms = [choice(terms_used_list) for _ in range(10)]

observed_expected = []
for term in comparison_terms:
    count_list = count_value(term)
    observed_expected.append(count_list)


# In[13]:


from scipy.stats import chisquare
import numpy as np

high_value_count = jeopardy[jeopardy["high_value"] == 1].shape[0]
low_value_count = jeopardy[jeopardy["high_value"] == 0].shape[0]

chi_squared = []

for items in observed_expected:
    total = sum(items)
    total_prop = total / jeopardy.shape[0]
    high = total_prop * high_value_count
    low = total_prop * low_value_count
    
    observed = np.array([items[0], items[1]])
    expected = np.array([high, low])
    chi_squared.append(chisquare(observed, expected))


# In[ ]:





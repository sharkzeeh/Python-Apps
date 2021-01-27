import pandas as pd
import re
from collections import Counter

def build_dict(file="lenta-ru-news.csv"):
    df = pd.read_csv(file, usecols = ["text"]).dropna()
    ok = df.text.str.contains("курс|курсом|курса|курсу|курсе", regex=True)
    dct = {}
    for article in df[ok].text:
        for sent in article.split('.'):
            split_sent = re.split(r'\W+|\d+', sent)
            while "" in split_sent:
                split_sent.remove("")
            for i in range(1, len(split_sent)):           
                cur_word = split_sent[i - 1].lower()
                next_word = split_sent[i].lower()
                if cur_word not in dct.keys():
                    dct[cur_word] = {}
                dct[cur_word][next_word] = dct[cur_word].get(next_word, 0) + 1
    return dct
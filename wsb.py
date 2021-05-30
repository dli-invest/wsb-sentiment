#!/usr/bin/env python
# coding: utf-8

# In[1]:


import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import praw
import matplotlib.pyplot as plt
import math
import datetime as dt
import pandas as pd
import numpy as np
import requests
import os
from io import StringIO

# In[2]:


nltk.download('vader_lexicon')
nltk.download('stopwords')


# In[3]:

client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
username = os.environ.get("REDDIT_USERNAME")
password = os.environ.get("REDDIT_PASSWORD")
url = os.environ.get("DISCORD_WEBHOOK")
reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret,
                    # user_name=
                    user_agent='dli-invest')


# In[4]:


sub_reddits = reddit.subreddit('wallstreetbets')
# stocks = ["BB", "GME", "AMC"]
stocks = ["SPCE", "LULU", "CCL", "SDC"]


# In[5]:


def commentSentiment(ticker, urlT):
    subComments = []
    bodyComment = []
    try:
        check = reddit.submission(url=urlT)
        subComments = check.comments
    except:
        return 0
    
    for comment in subComments:
        try: 
            bodyComment.append(comment.body)
        except:
            return 0
    
    sia = SIA()
    results = []
    for line in bodyComment:
        scores = sia.polarity_scores(line)
        scores['headline'] = line

        results.append(scores)
    
    df =pd.DataFrame.from_records(results)
    df.head()
    df['label'] = 0
    
    try:
        df.loc[df['compound'] > 0.1, 'label'] = 1
        df.loc[df['compound'] < -0.1, 'label'] = -1
    except:
        return 0
    
    averageScore = 0
    position = 0
    while position < len(df.label)-1:
        averageScore = averageScore + df.label[position]
        position += 1
    averageScore = averageScore/len(df.label) 
    
    return(averageScore)


# In[6]:


def latestComment(ticker, urlT):
    subComments = []
    updateDates = []
    try:
        check = reddit.submission(url=urlT)
        subComments = check.comments
    except:
        return 0
    
    for comment in subComments:
        try: 
            updateDates.append(comment.created_utc)
        except:
            return 0
    
    updateDates.sort()
    return(updateDates[-1])


# In[7]:


def get_date(date):
    return dt.datetime.fromtimestamp(date)


# In[8]:


submission_statistics = []
d = {}
for ticker in stocks:
    for submission in reddit.subreddit('wallstreetbets').search(ticker, limit=130):
        if submission.domain != "self.wallstreetbets":
            continue
        d = {}
        d['ticker'] = ticker
        d['num_comments'] = submission.num_comments
        d['comment_sentiment_average'] = commentSentiment(ticker, submission.url)
        if d['comment_sentiment_average'] == 0.000000:
            continue
        d['latest_comment_date'] = latestComment(ticker, submission.url)
        d['score'] = submission.score
        d['upvote_ratio'] = submission.upvote_ratio
        d['date'] = submission.created_utc
        d['domain'] = submission.domain
        d['num_crossposts'] = submission.num_crossposts
        d['author'] = submission.author
        submission_statistics.append(d)
    
dfSentimentStocks = pd.DataFrame(submission_statistics)

_timestampcreated = dfSentimentStocks["date"].apply(get_date)
dfSentimentStocks = dfSentimentStocks.assign(timestamp = _timestampcreated)

_timestampcomment = dfSentimentStocks["latest_comment_date"].apply(get_date)
dfSentimentStocks = dfSentimentStocks.assign(commentdate = _timestampcomment)

dfSentimentStocks.sort_values("latest_comment_date", axis = 0, ascending = True,inplace = True, na_position ='last') 

dfSentimentStocks


# In[9]:


dfSentimentStocks.author.value_counts()


# In[10]:


dfSentimentStocks.to_csv('Reddit_Sentiment_Equity.csv', index=False) 


def post_file_to_discord(url: str, file: str, filename: str = 'file'):
  url = url
  result = requests.post(
      url, files={filename: file}
  )

  try:
      result.raise_for_status()
  except requests.exceptions.HTTPError as err:
      print(err)
  else:
      print("Image Delivered {}.".format(result.status_code))

buffer = StringIO()  #creating an empty buffer
dfSentimentStocks.to_csv(buffer)  #filling that buffer
buffer.seek(0) #set to the start of the stream

post_file_to_discord(url, buffer, "Reddit_Sentiment_Equity.csv")
# In[ ]:
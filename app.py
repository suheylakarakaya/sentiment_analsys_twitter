from ast import keyword
from asyncio.windows_events import NULL
from pydoc import render_doc
from flask import Flask, render_template , request

import snscrape.modules.twitter as sntwitter
import pandas as pd
import csv

from asyncio.windows_events import NULL
from turtle import xcor
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch


app = Flask(__name__)

# ----------Get Tweets Start----------
def getTweets(search, limit = NULL):
    tweets = []
    #print(f'Limit Değeri:{limit}') f: stringin içine değişken ataması yaparken formata uygun olması için kullanılır.
    for tweet in sntwitter.TwitterSearchScraper(search).get_items():
        #print(vars(tweet))
        #break
        if limit == NULL:
            tweets.append([tweet.user.username, 
                           tweet.user.created.strftime("%Y-%m-%d"), 
                           tweet.user.followersCount, 
                           tweet.user.friendsCount, 
                           tweet.content, 
                           tweet.date.strftime("%Y-%m-%d"), 
                           tweet.replyCount, 
                           tweet.retweetCount,
                           tweet.likeCount,
                           tweet.url])
        
        else:
            if len(tweets) == limit:
                break
            else: 
                tweets.append([tweet.user.username, 
                           tweet.user.created.strftime("%Y-%m-%d"), 
                           tweet.user.followersCount, 
                           tweet.user.friendsCount, 
                           tweet.content, 
                           tweet.date.strftime("%Y-%m-%d"), 
                           tweet.replyCount, 
                           tweet.retweetCount,
                           tweet.likeCount,
                           tweet.url])

    #print(tweets)
    return tweets
# ----------Get Tweets End----------


# ----------Tweets to CSV Start----------
def getCSV(tweetList, username):
    df = pd.DataFrame(tweetList, columns=['username','user registration date', 'followers count', 'friends count', 'tweet', 'tweet date', 'reply count', 'retweet count', 'like count', 'tweet url' ])
    df.to_csv(username + '.csv', sep=';', encoding= 'utf-8-sig') 
# ----------Tweets to CSV End----------


# ----------Sentiment Analysis Start----------
def sentiment(tweets):
    tweet_words = []
    for x in tweets:
        for word in x[0].split(' '):
            if word.startswith('@') and len(word) > 1:
                word = '@user'

            elif word.startswith('http'):
                word = "http"
            tweet_words.append(word)

    tweet_proc = " ".join(tweet_words)
    # print(tweet_proc)
    # print(tweet_words)
    ###load model and tokenizer

    roberta = "cardiffnlp/twitter-roberta-base-sentiment"
    model = AutoModelForSequenceClassification.from_pretrained(roberta)
    tokenizer = AutoTokenizer.from_pretrained(roberta)
    labels = ['Negative', 'Neutral', 'Positive']

    ###sentiment analysis 
    encoded_tweet = tokenizer(tweet_proc, return_tensors='pt')
    #print(encoded_tweet)

    output = model(**encoded_tweet)

    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    for i in range(len(scores)):
        l = labels[i]
        s = scores[i]
        print(l,s)

    return labels, scores

# ----------Sentiment Analysis End----------



@app.route('/', methods =["GET", "POST"])
def hello_world():
    
    if request.method == "POST":
        username = request.form.get("username")
        key = request.form.get("keyword")
                
        #print(f'Keyword:{keyword}, len(keyword):{len(key)}')

        # twitter search syntax: "keyword (from:username)" 
        if(len(username) > 1 and len(key) > 1 ):
            filter = key + "(from:" +username+ ")"
            tweetler = getTweets(filter, 100)
            
            if(tweetler == []):
                return render_template('404.html')
            else: 
                getCSV(tweetler, username)
                status, values = sentiment(tweetler)
            
                return  render_template('response.html', tweetcount=len(tweetler), data = tweetler, labels=status, scores=values)
        
        elif(len(username) > 1 and len(key) == 0 ):
            filter ="(from:" +username+ ")"
            tweetler = getTweets(filter, 100)
            
            if(tweetler == []):
                return render_template('404.html')
            else: 
                getCSV(tweetler, username)
                status, values = sentiment(tweetler)
            
                return  render_template('response.html', data = tweetler, tweetcount=len(tweetler), labels=status, scores=values)

        else:
            return render_template('404.html')


    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)
import tweepy
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from textblob import TextBlob
#from config import *
import time
from os import environ

import seaborn as sns
from datetime import datetime
from pprint import pprint
from itertools import cycle

consumer_key = environ.get('consumer_key')
consumer_secret = environ.get('consumer_secret')
access_token = environ.get('access_token')
access_token_secret = environ.get('access_token_secret')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit=True)


query = '@SonikGryazzz'
accounts = [query]
last_tweet_id = 0

def two_plots(data,send,acc): # Callback: Creates plots from a data list
    df = pd.DataFrame(data)
    current_date = datetime.now().date().strftime("%d.%m.%Y")
    sns.set()
    
    feature_list = ['Polarity', 'Subjectivity']
    colors = cycle(['g', '#1a75ff'])
    
    plt.figure(figsize=(7,9))
    for i in range(len(feature_list)):
        
        plt.subplot(2,1,i+1)
        plt.plot(df['Tweets Ago'], df[feature_list[i]], marker='o', linewidth=0.3, color=next(colors), alpha=0.9)
        plt.title(f'Sentiment Analysis of {acc} Tweets {feature_list[i]}\n on {current_date}. Requested by {send}')
        plt.ylabel(f'Tweets {feature_list[i]}')
        plt.ylim(-1.1,1.1)
        
    plt.tight_layout()    
    plt.savefig('Output/plot.png')

def blob_sent(acc,send): # Callback: Gets data from a particular account and turns it into a list
    
    total_mood = []
    last_tweet = None
    tweet_counter = 0
    send = send
    acc = acc
    
    for x in range(3):
        
        all_data = api.user_timeline(acc, count=10, max_id=last_tweet, page=x)
        
        for tweet in all_data:
            
            blob = TextBlob(tweet['text'])
            sentiment = blob.sentiment
            total_mood.append({'Polarity': sentiment[0], 'Subjectivity': sentiment[1], 'Tweets Ago': tweet_counter}) 
            tweet_counter -= 1
            
        last_tweet = tweet["id"] - 1
    
    return two_plots(total_mood,send,acc)

def sentiment_bot(): # Main callback
    
    mentions = api.search(query, count=10, result_type='recent')
    print(len(mentions))
    
    for tweet in mentions['statuses']:
        tweet_id = tweet['id']
        print(f'tweet id: {tweet_id}')
        global last_tweet_id
        print(f'last id: {last_tweet_id}')
        
        if tweet_id > last_tweet_id:
            try:
                new_acc = (f'@{tweet["entities"]["user_mentions"][-1]["screen_name"]}')
                print(f'new acc to check: {new_acc}')
            
                if not new_acc:
                    break  
                
            except(IndexError):
                continue
            
            if new_acc not in accounts:
                accounts.append(new_acc)
                sender = (f"{tweet['user']['name']} (@{tweet['user']['screen_name']})")
                print(f'sender is {sender}')
                #print('---')
            
                blob_sent(new_acc, sender)
                #api.update_with_media('Output/plot.png', f'New Tweet Analysis of {new_acc}. Thank you {sender}!')
                api.update_with_media('Output/plot.png', f'New Tweet Analysis of .. Thank you ..!')
                print('plot printed')
            else:
                print('We\'ve analyzed it already')
                #print('---------')

    try:
        last_tweet_id = mentions['statuses'][0]['id']
        print(f'new last tweet id: {last_tweet_id}')
        
    except(IndexError):
        print('No new account name in the tweet')
    
while(True):    
    sentiment_bot()
    time.sleep(300)   

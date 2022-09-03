import snscrape.modules.twitter as sntwitter
import pandas as pd

query = "(from:elonmusk)"
tweets = []
limit = 1000

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
   
    # print(vars(tweet))
    # break

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

# df = pd.DataFrame(tweets, columns=['Url', 'Date', 'User', 'Tweet' ])
# print(df)

df = pd.DataFrame(tweets, columns=['username','user registration date', 'followers count', 'friends count', 'tweet', 'tweet date', 'reply count', 'retweet count', 'like count', 'tweet url' ])
df.to_csv('tweets.csv',encoding= 'utf-8-sig') 

#print(tweets)


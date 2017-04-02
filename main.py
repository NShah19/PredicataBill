from datetime import datetime
from trainingTweets import training_tweets
from sentimentAnalyzer import get_classifier, analyze
import re
import tweepy
import math
import nltk

consumer_key = '8n2xIVxdWhW661SSRkYMX5PWJ'
consumer_secret = 'Av9WibDlGyR5yGPvxzX7voxcXs2McHkDCFvZcqjP6nYvsYDcEa'

access_token = '848081359780302849-8UHyQfHoFhGMOVFIERZe07sEUORw3Vq'
access_token_secret = '92I4B67TMptFwuraWJKaPKvs9t4EEHzQr53w2EhFohX8a'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

INTRODUCTION_DATE = datetime(2017, 1 , 1)
VOTE_DATE = datetime(2017,4,2)
HANDLE_CSV = "sampleHandles.csv"
KW_CSV = "sampleKW.csv"
handleFile = open(HANDLE_CSV)
listOfHandles = []
for line in handleFile:
    listOfHandles.append(line[0:len(line) - 1])
kwFile = open(KW_CSV)
listOfKW = []
for line in kwFile:
    listOfKW.append(line[0:len(line) - 1].lower())
classifer = get_classifier(training_tweets)
tensorInputs = []

class Tweet(object):

    def __init__(self, tweetText, dateRep):
        self.text = tweetText.lower()
        self.sentiment = 0;
        self.date = dateRep

    def contains(self, kw_list):
        for kw in kw_list:
            if kw in self.text:
                return True
        return False

    def getDate(self):
        return self.date

    def getText(self):
        return self.text

    def setSentiment(self, n):
        self.sentiment = n

def isRelevant(tweet):
    if INTRODUCTION_DATE < tweet.getDate() and tweet.getDate() < VOTE_DATE and tweet.contains(listOfKW):
        return True
    return False

def weightedScore(sentiment_scores):
    numerator = 0
    denominator = 0
    for sentiment, date in sentiment_scores:
        maxDaysAway = (VOTE_DATE - INTRODUCTION_DATE).days + 1
        numDaysAway = (VOTE_DATE - date).days
        power = maxDaysAway - numDaysAway
        numerator += (sentiment * math.pow(1.2, power))
        denominator += math.pow(1.2, power)
    return numerator / denominator


for handle in listOfHandles:
    tweet_contents = []
    tweet_dates = []
    last_tweet_id = 0
    oldListOfTweets = []
    sentiment_scores = []
    # Get all user tweets that arent rts or replies
    try:
        user_tweets = api.user_timeline(screen_name=handle, count=200, include_rts=False, trim_user=True, exlude_replies=True)
        # loop 3200 times
        for i in range(0,15):
            for tweet in user_tweets:
                # append the cnotent of the tweet to 'tweet_contents' variable
                tweet_contents.append(tweet.text)
                # append the date of the tweet to 'tweet_dates' varable
                tweet_dates.append(tweet.created_at)
                # keep track of what tweet we are on by id
                last_tweet_id = tweet.id
                # perform sentiment analysis on the tweet
                score = analyze(tweet.text, classifer)
                sentiment_scores.append((score, tweet.created_at))
            # set the next tweets to parse through by making the
            user_tweets = api.user_timeline(screen_name=handle, max_id=last_tweet_id-1, count=200, include_rts=False, trim_user=True, exlude_replies=True)
        # create a Tweet object using the tweet contents and datetime object and append it to tweets
        for i in range(0,len(tweet_contents)):
            print(i)
            oldListOfTweets.append(Tweet(tweet_contents[i], tweet_dates[i]))
        listOfTweets = list(filter(isRelevant, oldListOfTweets));
        #sentiment analysis

    except tweepy.error.TweepError:
        pass

    # Add weighted sentiment score for each stream to the list of tensor inputs        
    tensorInputs.append(weightedScore(sentiment_scores))

print (tensorInputs)


#    getJSON from Twitter
#    parse JSON into list of up to 3200 Tweet objects
#    filter by keyword and date
#    get sentiment analysis score for this handle based on remaining tweets
#    add this scaled score to the list of inputs to tensorFlow
#
#run tensorFlow to get prediction probability

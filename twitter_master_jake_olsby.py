# -*-  utf-8 -*-
"""
Created on Sun Aug 12 11:41:07 2018

@author: jacob
"""

import tweepy
import pandas as pd
import collections
import datetime
from textblob import TextBlob
#place twitter_config in the same directory
#please use your own keys and secrets
import twitter_config

###############################################################################
# - Access and required intialization (Please use your own credentials)
###############################################################################

consumer_key = twitter_config.consumer_key
consumer_secret = twitter_config.consumer_secret

access_token_key = twitter_config.access_token_key
access_token_secret = twitter_config.access_token_secret

auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api=tweepy.API(auth)

##############################################################################
# Ideally Credentials would be put into a referenced file for security
##############################################################################

   
#-----------------------------------------------------------------------------
##############################################################################
# Screen_Name's Most Recent Tweets
##############################################################################
#-----------------------------------------------------------------------------

#Get tweets function, defaults to 100 most recent  
def get_tweets(screen_name = '@elonmusk'
               ,number_of_tweets = 100):
    '''
    A function to retrieve data around a users tweets
    for the most recent number of tweets. Defaulting as 100 tweets.
    Screen name, Tweet ID, Created Date Time, and Tweet text are loaded
    into newline-deliminated JSON format.
    '''
    
    #Had to add, tweetmode = extended, to get full length of tweets
    tweets = api.user_timeline(screen_name=screen_name
                               , count = number_of_tweets
                               , tweet_mode='extended')
    
    #the tweet and some details on the topic
    tweets_master = [[screen_name, tweet.id_str, tweet.created_at, tweet.full_text.encode('utf-8'), tweet.favorite_count] for tweet in tweets]
    
    for j in tweets_master:
        #looping through all the tweets
        j3 = str(j[3]).replace('"','').replace('\\','').replace("'",'')
        #stripping quotes and \ within text to make the JSON function as expected.
        #I realize I could scale this out better with Regex and the re package
        #but this seemed more direct, and less verbose for this need.
        #
        #get the sentiment analysis score of each tweet's text with TextBlob
        #simple Natural Language Processing (NLP) demonstration below
        # to demonstrate more interesting analysis
        sentiment_score = round(float(TextBlob(j3).sentiment.polarity), 2)
        #
        #JSON format below
        json = (f'''{{"screen_name": "{j[0]}","tweet_id": {j[1]},"created_datetime": "{j[2]}","tweet_favorite_count": {j[4]},"tweet_sentiment_score": {sentiment_score},"tweet_full_text": "{j3}"}},\n''')
        #append the JSON within the file for each tweets data
        #write it as JSON file type
        with open(f"{screen_name}_by_jake_olsby.json", "a") as myfile:
            myfile.write(json)
            
    print(f'Successfully wrote to JSON. Please see {screen_name}_by_jake_olsby.json\n')
    
#-----------------------------------------------------------------------------
##############################################################################
# Hashtag Analytics Finder Functions
##############################################################################
#-----------------------------------------------------------------------------

    
#function to find hashtags
def find_hashtags(tweet):
    '''
    A function to find associated with hashtags to our target hashtags.
    Cleans data and places them into a list for proper capture.
    '''    
    tweet_text = tweet
    #leading spaces
    tweet_text = tweet_text.replace('#', ' #')
    #remove clutter in tweet
    for punct in '.!",;:%<>/~`()[]{{}}?':
        tweet_text = tweet_text.replace(punct,'')
    #split out the tweet into a list of words
    tweet_text = tweet_text.split()
    #initialize empty to capture hashtags
    hashtag_list = []
    #loop over the words in the tweet
    for word in tweet_text:
        #find words that begin with a 'hashtag'=#
        if word[0]=='#':
            # Lower-case the word
            hashtag = word.lower()
            #Correct for possessives
            hashtag = hashtag.split('\'')[0]
            #remove the 'hashtag'=# symbol
            hashtag = hashtag.replace('#','')
            if len(hashtag)>0:
                hashtag_list.append(hashtag)
    return hashtag_list

    
#find associated hashtags     
def hashtag_searcher(target_hashtag='#Seattle'
                ,count_of_tweets = 100
                #default date is today's date (YYYY-MM-DD)
                #uses datetime module to get today's date
                ,to_date = datetime.datetime.today().strftime('%Y-%m-%d')
                ):
    '''
    A function to analyze tweets associated with a target hashtag.
    Defaults to the most recent 100 tweets and to todays date as YYYY-MM-DD.
    Target hashtag defaults to #Seattle but this can be easily changed.
    Essentially, a kind of market basket analysis but for hashtags.
    ''' 
    #simply hashtags to lower
    simple_hashtag = target_hashtag.lower()
    #remove the # to just the string
    simple_hashtag = simple_hashtag.replace('#', '')
                                            
    #create a empty list to capture new hashtags
    shared_tags = []
    
    #enable the Cursor to capture your parameters
    tweets = tweepy.Cursor(api.search
                           ,q = f"{target_hashtag}"
                           ,count = count_of_tweets
                           ,lang = "en"
                           ,since = to_date
                           ,tweet_mode ='extended'
                           ).items()
    
    #loop through tweets
    for tweet in tweets:
        
        #clean the tweet to get just the hashtags
        hashtags = find_hashtags(tweet.full_text)
        
        #iterate through the captured hashtags
        for tag in hashtags:
            #not our inputed hashtag
            if simple_hashtag not in tag:
                shared_tags.append(tag)
    
    #get the distribution of the items in the list
    tag_counts = collections.Counter(shared_tags)
    #turn into a dataframe
    df = pd.DataFrame.from_dict(tag_counts, orient='index')
    #sort by value
    df.columns = ['value']
    df = df.sort_values(by='value', ascending=False)
    #show Dataframe in console
    print(df)
    
    #Exported same data to excel to analyze and make decisions on!
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(f'{target_hashtag}_analysis_by_jake_olsby.xlsx'
                            , engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print(f'Successfully wrote to excel. Please see {target_hashtag}_analysis_by_jake_olsby.xlsx\n')

#-----------------------------------------------------------------------------
##############################################################################
# if __name__ == "__main__"
##############################################################################
#-----------------------------------------------------------------------------
    
if __name__ == "__main__":
    print("Executing as main program")
    print("Value of __name__ is: ", __name__)
    
    if(api.verify_credentials):
        print('We successfully logged in.\n')
    #Part 1
    print('Starting Part 1 of Twitter Python Script by Jake Olsby...\n')
    get_tweets()
    #Part 2
    print('Starting Part 2 of Twitter Python Script by Jake Olsby...\n')
    hashtag_searcher()
    

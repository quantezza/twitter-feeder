#
import os
from flask import Flask,jsonify
import threading
import time
from TwitterAPI import TwitterAPI, TwitterRestPager
from yaml import load, dump
import json
from kafka import SimpleProducer, KafkaClient
import traceback
import sys

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN_KEY = ''
ACCESS_TOKEN_SECRET = ''
KAFKA_BROKER=''

SEARCH_TERM = 'docker'

twitter_metrics = {}
twitter_metrics["tweets-consumed"] = 0

def tweet_producer():
    kafka = KafkaClient(KAFKA_BROKER)
    producer = SimpleProducer(kafka)
    while True:
        try:
            api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

            print('Using search term: %s' % SEARCH_TERM)
            pager = TwitterRestPager.TwitterRestPager(api, 'search/tweets', {'q': SEARCH_TERM})
            for item in pager.get_iterator():
                if 'text' in item:
                    tweet = {}
                    # tweet['coordinates'] = item['coordinates']
                    #rhoover: the mktime/strptime below is incorrect (making times in the future) so using this for now
                    tweet['@timestamp'] = int(time.time() * 1000.0)
                    # tweet['@timestamp'] = time.mktime(time.strptime(item['created_at'],"%a %b %d %H:%M:%S +0000 %Y")) * 1000
                    # tweet['place'] = item['place']
                    # ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(item['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

                    # tweet['@timestamp'] = item['created_at']
                    tweet['username'] = item['user']['name']
                    tweet['handle'] = item['user']['screen_name']
                    tweet['lang'] = item['lang']
                    tweet['timezone'] = item['user']['time_zone']
                    tweet['followers'] = item['user']['followers_count']
                    tweet['location'] = item['user']['location']
                    tweet['retweeted'] = item['retweeted']
                    tweet['text'] = item['text']
                    producer.send_messages(b'tweets', bytes(json.dumps(tweet), "UTF-8"))
                    twitter_metrics["tweets-consumed"] = twitter_metrics["tweets-consumed"] + 1
                elif 'message' in item and item['code'] == 88:
                     print('SUSPEND, RATE LIMIT EXCEEDED: %s\n' % item['message'])
                     time.sleep(120)
                     break
                print('Consumed %s tweets' % twitter_metrics["tweets-consumed"])
        except:
            print(traceback.format_exc())
            print("Sleeping for 120 secs.")
            time.sleep(120)
    return

if __name__ == '__main__':

    api_key = open(os.environ['SECRET_DIR'] + '/twitter-secret.yaml')
    data = load(api_key)
    api_key.close()
    print(data)

    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']
    ACCESS_TOKEN_KEY = data['ACCESS_TOKEN_KEY']
    ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
    KAFKA_BROKER=os.environ['KAFKA_BROKER_SERVICE_HOST'] + ":" + os.environ['KAFKA_BROKER_SERVICE_PORT']
    print("KAFKA_BROKER=" + KAFKA_BROKER)

    tweet_producer()

import os
from flask import Flask,jsonify
import threading
import time
from TwitterAPI import TwitterAPI, TwitterRestPager
from yaml import load, dump
import json
from kafka import SimpleProducer, KafkaClient

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN_KEY = ''
ACCESS_TOKEN_SECRET = ''

SEARCH_TERM = 'docker'

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)

twitter_metrics = {}
twitter_metrics["tweets-consumed"] = 0

def tweet_producer():

    api = TwitterAPI(CONSUMER_KEY,
                     CONSUMER_SECRET,
                     ACCESS_TOKEN_KEY,
                     ACCESS_TOKEN_SECRET)

    pager = TwitterRestPager.TwitterRestPager(api, 'search/tweets', {'q': SEARCH_TERM})
    for item in pager.get_iterator():
        if 'text' in item:
            tweet = {}
            # tweet['coordinates'] = item['coordinates']
            tweet['@timestamp'] = time.mktime(time.strptime(item['created_at'],"%a %b %d %H:%M:%S +0000 %Y")) * 1000
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
    return

app = Flask(__name__)

@app.route('/', methods=['GET'])
def status():
    status = {}
    status["metrics"] = twitter_metrics
    status["env"] = {str(key) : str(os.environ[key]) for  key in os.environ.keys() }
    return jsonify(status)

if __name__ == '__main__':

    # api_key = open('/etc/secret-volume/twitter-secret.yaml')
    api_key = open('/Users/arrawatia/code/try-openshift/template/twitter-secret.yaml')
    data = load(api_key)
    api_key.close()
    print(data)

    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']
    ACCESS_TOKEN_KEY = data['ACCESS_TOKEN_KEY']
    ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']

    tweet_feeder= threading.Thread(name="Tweet producer", target=tweet_producer)
    tweet_feeder.daemon = True
    tweet_feeder.start()

    app.run(debug=True)

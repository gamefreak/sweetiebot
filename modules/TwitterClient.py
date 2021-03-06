import requests
import time
from base64 import b64encode
import logging
from utils import logerrors

log = logging.getLogger(__name__)

def get_client(key, secret):
    url = 'https://api.twitter.com/oauth2/token'
    headers = {
        'Authorization': 'Basic '+b64encode((key+':'+secret).encode('utf-8')).decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    data = { 'grant_type': 'client_credentials' }
    response = requests.post(url, headers=headers, data=data).json()
    token_type = response['token_type']
    token = response['access_token']
    return TwitterClient(token)

class TwitterClient:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def get_timeline_watcher(self, username):
        watcher = TimelineWatcher(self.bearer_token, username)
        watcher.get_next_tweet()
        return watcher

# TODO: we'll probably want a search watcher as well (eg #sweetiebot)
# which will share a bunch of code here

class TimelineWatcher:
    def __init__(self, bearer_token, username):
        self.bearer_token = bearer_token
        self.username = username
        self.latest_tweet = None

    @logerrors
    def get_timeline(self, since_id, count):
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        data = {
            'screen_name': self.username,
            #'exclude_replies': 'true',
            #'include_rts': 'false',
        }
        if since_id is not None: data['since_id'] = since_id
        if count is not None: data['count'] = count

        headers = {
            'Authorization': 'Bearer '+self.bearer_token,
        }

        response = requests.get(url, params=data, headers=headers).json()
        return response

    @logerrors
    def get_next_tweet(self):
        # we don't actually want any tweets for our first request -
        # we're just discarding earlier tweets
        should_return = self.latest_tweet is not None

        tweets = self.get_timeline(self.latest_tweet, 1)
        #print(str(tweet))

        if tweets:
            if isinstance(tweets, str):
                raise Exception(tweets)
            #print(tweet[0]['text'])
            tweet = tweets[0]
            self.latest_tweet = tweet['id']
            #print('setting latest tweet to '+str(self.latest_tweet))
            if should_return:
                return tweet['text']

if __name__ == '__main__':
    import config
    logging.basicConfig(level=logging.DEBUG)
    client = get_client(config.twitter_key, config.twitter_secret)
    #watcher = client.get_timeline_watcher('EVE_Status')
    watcher = client.get_timeline_watcher('RedScareBot')
    while True:
        tweet = watcher.get_next_tweet()
        if tweet: print(str(tweet['text']))
        time.sleep(10)


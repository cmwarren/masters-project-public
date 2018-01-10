
# -*- coding: utf-8 -*-
from twitter import *
import twitter
import codecs
import pause
import datetime as dt
import dateutil.parser
import json
import pprint
from nltk.tokenize import TweetTokenizer
import urllib2
import httplib


class MyTwitterBase:
    def __init__(self):
        # Manage these settings at https://apps.twitter.com
        self.auth = OAuth(
            token='219274156-ixItRHA7spMqsI2mgFc8EnBCe6cZbsPp3EKun2KI',
            token_secret='qL6ipM07UgE6xajpVhAqlLGauuo8rgjuaM7yYICLzzKg6',
            consumer_key='9JbZogINp4D3M5QNn1zEKlPDS',
            consumer_secret='QJcZ6O08byBxeN9I7in8qCABJAmNKV7Jjg3SmZqMr5GhgZ5iEW')

        self.tokenizer = TweetTokenizer()

    @staticmethod
    def status_to_string(status, include_rt, include_qs):
        if 'retweeted_status' in status:
            if include_rt:
                return status['retweeted_status']['text'].replace('\n', ' ')
            else:
                return None
        if 'quoted_status' in status:
            if include_qs:
                return status['quoted_status']['text'].replace('\n', ' ')
            else:
                return None
        if 'text' in status:
            return status['text'].replace('\n', ' ')


class MyTwitterApiClient(MyTwitterBase):

    rate_limits = None

    # Use singleton pattern to maintain rate limit state
    __instance = None

    def __new__(cls, val):
        if MyTwitterApiClient.__instance is None:
            MyTwitterApiClient.__instance = object.__new__(cls)
            MyTwitterApiClient.__instance.val = val
        return MyTwitterApiClient.__instance

    def __init__(self):
        MyTwitterBase.__init__(self)

        self.deserialize_rate_limits()

        # REST API - Initialise client
        self.t = Twitter(auth=self.auth)

    def __del__(self):
        # TODO - Make this thread-safe?  Would need to serialize again each time count is incremented
        self.serialize_rate_limits()

    # Methods to manage rate limits

    def init_rate_limits(self):
        # Set up rate limits for the first time
        self.rate_limits = {
            # Search API - Rate limit: 180 / 15 mins
            'search': {'start': dt.datetime.now(), 'count': 0, 'limit': 180, 'period': 15.25},
            'application': {'start': dt.datetime.now(), 'count': 0, 'limit': 180, 'period': 15.25}
        }

    def check_rate_limit(self, api):
        rate_count = self.rate_limits[api]['count']
        rate_limit = self.rate_limits[api]['limit']
        rate_start = self.rate_limits[api]['start']
        rate_period = self.rate_limits[api]['period']

        rate_end = rate_start + dt.timedelta(minutes=rate_period)
        now = dt.datetime.now()

        if rate_end > now:
            if rate_count >= rate_limit:
                raise RateLimitError(api, rate_end)
        else:
            self.rate_limits[api]['start'] = now
            self.rate_limits[api]['count'] = 0
            print('API=' + api + ' - Resetting rate period start time: ' + str(now))

    def increment_rate_count(self, api):
        count = self.rate_limits[api]['count']
        count += 1
        self.rate_limits[api]['count'] = count

        self.serialize_rate_limits()
        print('API=' + api + ', rate_count=' + str(self.rate_limits[api]['count']))

    def deserialize_rate_limits(self):
        # Deserialize rate limit state
        try:
            with open('./rate_limits.txt', 'r') as f:
                self.rate_limits = json.load(f, object_pairs_hook=self.load_with_datetime)
        except (IOError, EOFError):
            self.init_rate_limits()

        if self.rate_limits is None:
            self.init_rate_limits()

    def serialize_rate_limits(self):
        # Serialize rate limit state
        with open('./rate_limits.txt', 'w') as f:
            json.dump(self.rate_limits, f, default=lambda obj: obj.isoformat() if hasattr(obj, 'isoformat') else obj)

    def load_with_datetime(self, pairs):
        """Load with dates"""
        d = {}
        for k, v in pairs:
            if isinstance(v, basestring):
                try:
                    d[k] = dateutil.parser.parse(v)
                except ValueError:
                    d[k] = v
            else:
                d[k] = v
        return d

    # API calling methods

    def search_tweets(self, lang_code, query, max_count=10):

        try:
            self.check_rate_limit('search')

            # Search for 'recent' or 'popular' tweets matching a query
            tweets = self.t.search.tweets(q=query, lang=lang_code, result_type='mixed',
                                          count=max_count, include_entities=False)

            self.increment_rate_count('search')
        except RateLimitError as e:
            print('API=' + e.api + ' - Rate limit exceeded: sleeping until ' + str(e.rate_end))
            pause.until(e.rate_end)
            tweets = self.search_tweets(lang_code, query, max_count)

        return tweets

    # File extraction methods

    def output_tweets(self, lang_code, query, filename, sent_counter, max_count=10):

        b_tweets_output = False

        try:
            tweets = self.search_tweets(lang_code, query, max_count)

        except twitter.api.TwitterHTTPError as er:
            # Local rate limit cache has probably got out of synch with Twitter
            print("TwitterHTTPError: " + str(er))
            self.synchronise_rate_limit()  # Re-synchronise and retry
            tweets = self.search_tweets(lang_code, query, max_count)

        except (urllib2.URLError, httplib.BadStatusLine) as er:
            # Connection dropped
            print("Connection error: " + str(er))
            pause.sleep(15)  # Sleep 15 seconds and retry
            try:
                tweets = self.search_tweets(lang_code, query, max_count)
            except urllib2.URLError as er:
                print("Connection error: " + str(er))
                pause.sleep(30)  # Sleep 30 seconds and retry again
                tweets = self.search_tweets(lang_code, query, max_count)

        f = codecs.open(filename, 'a', encoding='utf-8', errors='replace')

        for status in tweets['statuses']:
            status_str = MyTwitterBase.status_to_string(status, False, False)
            if status_str is not None:
                if query.lower() in status_str.lower():
                    tokens = self.tokenizer.tokenize(status_str)
                    # print(status_str)
                    b_tweets_output = True
                    #f.write(query + ' ||| ' + status_str + '\n')
                    f.write(lang_code + str(sent_counter) + '\t' + ' '.join(tokens).lower() + '\n')
                    sent_counter += 1
        f.close()

        return [b_tweets_output, sent_counter]

    def synchronise_rate_limit(self):

        rate_limit_response = self.t.application.rate_limit_status(resources='search,application')
        pprint.pprint(rate_limit_response)

        app_resource = rate_limit_response['resources']['application']['/application/rate_limit_status']
        search_resource = rate_limit_response['resources']['search']['/search/tweets']

        self.rate_limits['application']['count'] = app_resource['limit'] - app_resource['remaining']
        self.rate_limits['search']['count'] = search_resource['limit'] - search_resource['remaining']


        self.rate_limits['application']['start'] = dt.datetime.fromtimestamp(app_resource['reset']) \
                                                   - dt.timedelta(minutes=self.rate_limits['application']['period'])
        self.rate_limits['search']['start'] = dt.datetime.fromtimestamp(search_resource['reset']) \
                                              - dt.timedelta(minutes=self.rate_limits['search']['period'])

        self.serialize_rate_limits()

        return rate_limit_response


class MyTwitterStreamClient(MyTwitterBase):

    # TODO - What do I need to do to manage rate limits for streaming?

    def __init__(self):
        MyTwitterBase.__init__(self)

        # Streaming API - Track tweets based on a filter
        self.public_stream = TwitterStream(auth=self.auth, domain='stream.twitter.com')

    def stream_tweets_to_file(self, lang_code, query, filename, max_count=10):
        count = 0
        f = codecs.open(filename, 'w', encoding='utf-8')

        for status in self.public_stream.statuses.filter(track=query, language=lang_code):
            if count > max_count:
                break
            status_str = MyTwitterBase.status_to_string(status, False, False)
            if status_str is not None:
                # print(status_str)
                f.write(status_str + '\n')
                count += 1
        f.close()


class RateLimitError(RuntimeError):

    def __init__(self, api, rate_end):
        self.api = api
        self.rate_end = rate_end
        self.message = 'Rate limit exceeded: API=' + api + ', period ends ' + str(self.rate_end)

    pass

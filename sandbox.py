#! -*- coding: utf-8 -*-

import twitter
import os
import json

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN_KEY = ''
ACCESS_TOKEN_SECRET = ''

RAW_TWEET_OUTPUT_DIR = os.environ.get("HOME") + '/devel/happyday/tweet_raw'

#検索対象のハッシュタグ一覧
QUERY_HASH_TAGS=['#dreammap', '#チョコの代わりにメッセージ ']



Base = declarative_base()
engine = create_engine("mysql://mak:paramore@versa/happyday2016", encoding='utf-8', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# twitter_tweet モデル
class TwitterTweet(Base):
    __tablename__ = 'twitter_tweet'

    tweet_id = Column(String, primary_key=True)
    create_at = Column(DateTime)
    create_at_str = Column(String)
    user_id = Column(String)
    user_name = Column(String)
    text = Column(Text)
    enabled = Column(Boolean)

    def __init__(self, tweet_id, create_at, create_at_str, user_id, user_name, text, enabled):
        self.tweet_id = tweet_id
        self.create_at = create_at
        self.create_at_str = create_at_str
        self.user_id = user_id
        self.user_name = user_name
        self.text = text
        self.enabled = enabled

# twitter_hashtag モデル
class TwitterHashtag(Base):
    __tablename__ = 'twitter_hashtag'

    hashtag = Column(String, primary_key=True)
    tweet_id = Column(String, primary_key=True)


    def __init__(self, hashtag, tweet_id):
        self.tweet_id = tweet_id
        self.hashtag = hashtag

# twitter_media モデル
class TwitterMedia(Base):
    __tablename__ = 'twitter_media'

    tweet_id = Column(String)
    media_id = Column(String, primary_key=True)
    type = Column(String)
    media_url = Column(String)
    media_url_https = Column(String)


    def __init__(self, tweet_id, media_id, type, media_url, media_url_https):
        self.tweet_id = tweet_id
        self.media_id = media_id
        self.type = type;
        self.media_url = media_url
        self.media_url_https = media_url_https

def insert_tweet(tweet_raw):

    tweet_dict = tweet_raw.AsDict()
    print (str(tweet_raw.GetId()))

    print(tweet_raw.GetId())
    print(tweet_raw.GetCreatedAt())
    print(tweet_raw.GetUser().GetId())

    tweet = TwitterTweet(str(tweet_raw.GetId()),
                  datetime.strptime(tweet_raw.GetCreatedAt(), '%a %b %d %X +0000 %Y'),
                  tweet_raw.GetCreatedAt(),
                  str(tweet_raw.GetUser().GetId()),
                  tweet_raw.GetUser().GetName(),
                  tweet_raw.GetText(),
                  True
                  )

    session.add(tweet)
    # SEE 毎回flushしなければいけない。
    # <https://hiroakis.com/blog/2014/03/24/python-sqlalchemyでちょっとハマったこと/>
    session.flush()

    for tag in tweet_dict['hashtags']:
        hashtag = TwitterHashtag(tag, str(tweet_raw.GetId()))
        session.add(hashtag)
        session.flush()

    for media in tweet_dict['media']:
        media = TwitterMedia(str(tweet_raw.GetId()), media['id_str'], media['type'], media['media_url'], media['media_url_https'])
        session.add(media)
        session.flush()

    session.commit()



def collect_tweets():
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)
    ret = api.VerifyCredentials()


    print(ret)
    print(api.GetRateLimitStatus())

    q = ' OR '.join(QUERY_HASH_TAGS)
    print(q)

    ret = api.GetSearch(count=100, term=q)

    total = 0
    for r in ret:

        # リツイートの場合は何もしない
        if 'retweeted_status' in r.AsDict():
            continue

        # 画像などメディアが貼付けられていなければ何もしない
        if 'media' not in r.AsDict():
            continue

        # 動画などの場合は無視
        is_photo = False
        for media in r.AsDict()['media']:
            if media['type'] == 'photo':
                is_photo = True
        if is_photo == False:
            continue

        # 生tweetをファイル保存する
        of = open(RAW_TWEET_OUTPUT_DIR + '/' + str(r.id) + '.json', 'w')
        of.write(json.dumps(json.loads(r.AsJsonString()), indent=2))
        of.close()

        insert_tweet(r)
        total = total + 1

        for medias in r.AsDict()['media']:

            print('===S')
            print(r.id)
            print medias['media_url']
            print('===E')

    print total

def main():
    print('start main method.')

    collect_tweets()


if __name__ == '__main__':
    print('start')

    main()

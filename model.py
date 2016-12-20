#! -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
    screen_name = Column(String)

    def __init__(self, tweet_id, create_at, create_at_str, user_id, user_name, text, enabled, screen_name):
        self.tweet_id = tweet_id
        self.create_at = create_at
        self.create_at_str = create_at_str
        self.user_id = user_id
        self.user_name = user_name
        self.text = text
        self.enabled = enabled
        self.screen_name = screen_name


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
    enabled = Column(Boolean)

    def __init__(self, tweet_id, media_id, type, media_url, media_url_https, enabled):
        self.tweet_id = tweet_id
        self.media_id = media_id
        self.type = type
        self.media_url = media_url
        self.media_url_https = media_url_https
        self.enabled = enabled

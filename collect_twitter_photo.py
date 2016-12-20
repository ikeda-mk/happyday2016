#! -*- coding: utf-8 -*-

import twitter
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from model import TwitterMedia, TwitterHashtag, TwitterTweet

from logging import getLogger
import logging.config
import loggingconfig
import config

logging.config.dictConfig(loggingconfig.LOGGING_CONFIG)

log = getLogger(__name__)

CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
ACCESS_TOKEN_KEY = config.ACCESS_TOKEN_KEY
ACCESS_TOKEN_SECRET = config.ACCESS_TOKEN_SECRET


# 検索対象のハッシュタグ一覧
QUERY_HASH_TAGS = config.TWITTER_HASH_TAG

SEARCH_DEPTH = 10

Base = declarative_base()
engine = create_engine(
    "mysql://%s:%s@%s/%s?charset=utf8" % (config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_NAME),
    encoding='utf-8', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


def insert_tweet(tweet_raw):
    log.info("start transaction [%s]" % tweet_raw.GetId())

    try:
        tweet_dict = tweet_raw.AsDict()
        log.debug(str(tweet_raw.GetId()))

        log.debug(tweet_raw.GetId())
        log.debug(tweet_raw.GetCreatedAt())
        log.debug(tweet_raw.GetUser().GetId())

        hits = session.query(TwitterTweet.tweet_id).filter(TwitterTweet.tweet_id == str(tweet_raw.GetId())).count()
        log.debug("%s : hits count [%s]" % (tweet_raw.GetId(), hits))
        if hits > 0:
            return

        log.debug(tweet_raw.AsDict()['user']['screen_name'])

        tweet = TwitterTweet(str(tweet_raw.GetId()),
                             datetime.strptime(tweet_raw.GetCreatedAt(), '%a %b %d %X +0000 %Y'),
                             tweet_raw.GetCreatedAt(),
                             str(tweet_raw.GetUser().GetId()),
                             tweet_raw.GetUser().GetName(),
                             tweet_raw.GetText(),
                             True,
                             tweet_raw.AsDict()['user']['screen_name'])

        session.add(tweet)
        # NOTE 毎回flushしなければいけない。
        # <https://hiroakis.com/blog/2014/03/24/python-sqlalchemyでちょっとハマったこと/>
        session.flush()

        # 検索条件のハッシュタグ以外はDB保存しない。
        for tag in tweet_dict['hashtags']:
            for query_tag in QUERY_HASH_TAGS:
                if '#' + tag.lower() == query_tag.lower():
                    hashtag = TwitterHashtag(tag, str(tweet_raw.GetId()))
                    session.add(hashtag)
                    session.flush()

        for media in tweet_dict['media']:
            # delete / insert

            hits = session.query(TwitterMedia).filter(TwitterMedia.media_id == media['id_str']).count()

            if hits > 0:
                rows = session.query(TwitterMedia).filter(TwitterMedia.media_id == media['id_str']).all()
                for row in rows:
                    session.delete(row)
                    session.flush()

            media = TwitterMedia(str(tweet_raw.GetId()), media['id_str'], media['type'], media['media_url'],
                                 media['media_url_https'], True)
            session.add(media)
            session.flush()

        session.commit()
    except:
        log.error("rollback tweet_id is [%s]" % (tweet_raw.GetId()), exc_info=True)
        session.rollback()


def store_search_result(search_result):
    for r in search_result:

        log.debug('tweet_id is %s' % str(r.id))

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
        if not is_photo:
            continue

        # 生tweetをファイル保存する
        of = open(config.RAW_TWEET_OUTPUT_DIR + '/' + str(r.id) + '.json', 'w')
        of.write(json.dumps(json.loads(r.AsJsonString()), indent=2))
        of.close()

        insert_tweet(r)


def collect_tweets():
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)
    ret = api.VerifyCredentials()

    log.debug(ret)
    log.debug(api.GetRateLimitStatus())

    q = ' OR '.join(QUERY_HASH_TAGS)
    log.debug(q)

    ret = api.GetSearch(count=100, term=q)
    store_search_result(ret)

    for d in range(SEARCH_DEPTH):
        since_id = ret[-1].GetId()
        log.info("since_id = %s" % since_id)
        ret = api.GetSearch(count=100, term=q, max_id=since_id)
        log.debug('result count = %s' % len(ret))
        if len(ret) == 0:
            break

        store_search_result(ret)

        if len(ret) < 100:
            break


def main():
    log.debug('start main method.')

    collect_tweets()


if __name__ == '__main__':
    main()

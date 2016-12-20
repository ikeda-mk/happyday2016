#! -*- coding: utf-8 -*-

from logging import getLogger
import logging.config
import loggingconfig
import config
logging.config.dictConfig(loggingconfig.LOGGING_CONFIG)

log = getLogger(__name__)

from model import TwitterHashtag, TwitterMedia, TwitterTweet

from sqlalchemy.sql import select, join, func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("mysql://%s:%s@%s/%s?charset=utf8" % (config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_NAME), encoding='utf-8', echo=True)
connection = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()


def disable_tweet(hashtag):
    q = select([TwitterHashtag.tweet_id]).where(TwitterHashtag.hashtag == hashtag)
    log.debug(q)

    tweet_ids = []

    for r in connection.execute(q).fetchall():
        tweet_ids.append(r['tweet_id'])

        records = session.query(TwitterTweet).filter(TwitterTweet.tweet_id == r['tweet_id']).all()

        for row in records:
            log.debug(row.tweet_id)
            log.debug(row.user_id)

            tweet_url = "https://twitter.com/%s/status/%s" % (row.user_id, row.tweet_id)
            code = http_get(tweet_url)
            log.info("%s, %s" % (tweet_url, code))

            if code != 200:
                row.enabled = False

                session.add(row)
                session.commit()


def select_media(hashtag):

    j = join(TwitterMedia, TwitterHashtag, TwitterMedia.tweet_id == TwitterHashtag.tweet_id)
    q = select([TwitterMedia.media_url, TwitterMedia.tweet_id]).where(TwitterHashtag.hashtag == hashtag).where(TwitterMedia.enabled == True).select_from(j)

    log.debug(q)

    result = []

    for r in connection.execute(q).fetchall():
        result.append(r['media_url'])

    return result


def http_get(url):
    import urllib

    log.debug(url)
    ret = urllib.urlopen(url)
    #ret.close
    log.debug('%s, %s' % (ret.code, url))

    return ret.code


def disable_media(url):
    record = session.query(TwitterMedia).filter(TwitterMedia.media_url == url).one()
    print(record)
    record.enabled = False

    session.add(record)

    session.commit()


def main():

    for tag in config.TWITTER_HASH_TAG:
        disable_tweet(tag.split("#")[1])

        medias = select_media(tag.split('#')[1])

        for media in medias:
            code = http_get(media)
            if code != 200:
                log.info(media)

                disable_media(media)


if __name__ == '__main__':
    main()
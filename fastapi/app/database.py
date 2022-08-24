from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import VIDEO_SHARDS_QUANTITY, HISTORY_SHARDS_QUANTITY, VIDEO_SHARD_KEY, HISTORY_SHARD_KEY

sessions = {}
SQLALCHEMY_DEFAULT_DATABASE_URL = "postgresql://user:password@db:5432/default_db"

engine = create_engine(SQLALCHEMY_DEFAULT_DATABASE_URL)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sessions['default_db'] = session

for i in range(1, VIDEO_SHARDS_QUANTITY + 1):
    db_key = 'video_shard_%d' % i
    url = "postgresql://user:password@db:5432/%s" % db_key
    engine_loc = create_engine(url)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine_loc)
    sessions[db_key] = session

for i in range(1, HISTORY_SHARDS_QUANTITY + 1):
    db_key = 'history_shard_%d' % i
    url = "postgresql://user:password@db:5432/%s" % db_key
    engine_loc = create_engine(url)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine_loc)
    sessions[db_key] = session

Base = declarative_base()

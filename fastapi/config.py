VIDEO_SHARDS_QUANTITY = 5
HISTORY_SHARDS_QUANTITY = 3

VIDEO_SHARD_KEY = 'video_shard_%d'
HISTORY_SHARD_KEY = 'history_shard_%d'


class Foo:
    def __init__(self):
        self.x = 1

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.x)


with Foo() as f:
    print(f.x)
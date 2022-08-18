from django.db.models import QuerySet
from django.conf import settings


class ShardQuerySet(QuerySet):
    use_for_related_fields = True

    def chain_shard(self, shard_id):
        if shard_id is not None:
            db = self.get_db(shard_id)
            if self.db != db:
                return super().using(db)
        return super()

    def extract_shard_id(self, kwargs):
        return (kwargs.pop("shard_id") if "shard_id" in kwargs else None), kwargs

    def filter(self, *args, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).exclude(*args, **kwargs)

    def all(self, shard_id=None):
        return self.chain_shard(shard_id).all()

    def get(self, *args, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).get(*args, **kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).get_or_create(defaults=defaults, **kwargs)

    def create(self, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).create(**kwargs)

    def update(self, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).update(**kwargs)

    def bulk_create(self, *args, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).bulk_create(*args, **kwargs)

    def bulk_update(self, *args, **kwargs):
        shard_id, kwargs = self.extract_shard_id(kwargs)
        return self.chain_shard(shard_id).bulk_update(*args, **kwargs)


class VideoShardQuerySet(ShardQuerySet):
    def get_db(self, category_id):
        return settings.DATABASE_VIDEO_DRIVE_KEY % category_id


class HistoryShardQuerySet(ShardQuerySet):
    def get_db(self, user_id):
        return settings.DATABASE_HISTORY_DRIVE_KEY % (user_id % 3 + 1)

    # def get_videos_by_user(self, user_id, category_id):
    #     return self.chain_shard(shard_id=user_id).filter(video_id__startswith=f'{category_id}__')

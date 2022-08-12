from django.db import models
from uuid import uuid4
from content.models import HistoryShardQuerySet, Category, Video


class History(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False, unique=True)

    user_id = models.IntegerField(blank=False, null=False)
    """ SCHEMA: shard_id__video_id"""
    video_id = models.CharField(max_length=255, blank=False, null=False)

    objects = HistoryShardQuerySet.as_manager()

    def parse_video_id(self):
        category_id, video_id = self.video_id.split('__')
        return category_id, video_id

    def get_category_and_video(self):
        category_id, video_id = self.parse_video_id()
        category = Category.objects.get(id=category_id)
        video = Video.objects.get(shard_id=category_id, id=video_id)

        return category, video

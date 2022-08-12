from django.db import models, IntegrityError
from uuid import uuid4
import random
import string
from django.utils.timezone import now
from content.models.querysets import VideoShardQuerySet
from content.models.tag import Tag
from content.models.category import Category


def get_r_id():
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.sample(chars, 6))


class Video(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    r_id = models.CharField(default=get_r_id, unique=True, max_length=10)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=now)

    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)

    category = models.CharField(max_length=255, null=True, blank=True)  # id representation of category
    tags = models.JSONField(default=list, null=False, blank=False)  # list of tags id

    objects = VideoShardQuerySet.as_manager()

    def __str__(self):
        return self.r_id

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        try:
            super().save(force_insert, force_update, using, update_fields)
        except IntegrityError:
            self.r_id = get_r_id()
            self.save(force_insert, force_update, using, update_fields)

    def get_tags_qs(self):
        tags = self.tags
        qs = Tag.objects.filter(id__in=tags)
        return qs

    def get_category(self):
        category = Category.objects.get(id=self.category)
        return category


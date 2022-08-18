from django.core.management import BaseCommand
from django.conf import settings
from content.models import Video
from content.documents import VideoDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        shards = settings.DATABASE_VIDEO_SHARDS_QUANTITY

        for i in range(1, shards + 1):
            qs = Video.objects.chain_shard(i).all()
            VideoDocument().update(qs)

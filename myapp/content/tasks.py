from celery import shared_task
from django.core.cache import cache
from content.utils import ViewsService, RecommendationsService, generate_rec_cache_key


@shared_task
def process_view(user_id, video_id, category_id):
    service = ViewsService(user_id, video_id, category_id)
    service.process_view()


@shared_task
def calculate_recommendations(user_id):
    service = RecommendationsService(user_id)
    service.process()
    cache_key = generate_rec_cache_key(user_id)
    cache.set(cache_key, service.result)

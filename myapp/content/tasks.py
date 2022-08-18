from celery import shared_task
from django.core.cache import cache
from content.utils import ViewsService, RecommendationsService


@shared_task
def process_view(user_id, video_id, category_id):
    service = ViewsService(user_id, video_id, category_id)
    service.process_view()


@shared_task
def calculate_recommendations(user_id):
    service = RecommendationsService(user_id)
    result = service.process()
    print(f'>> FROM task, user_id: {user_id}, type: {type(user_id)}')
    cache.set(user_id, result)
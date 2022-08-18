from content.documents import VideoDocument
from elasticsearch_dsl import Q
from django.conf import settings


def es_search(title: str, description: str) -> list:
    result = []

    q1 = Q('multi_match', query=title, fields=['title'])
    q2 = Q('multi_match', query=description, fields=['description'])

    for i in range(1, settings.DATABASE_VIDEO_SHARDS_QUANTITY + 1):
        search = VideoDocument.search(db=settings.DATABASE_VIDEO_DRIVE_KEY % i)
        if title:
            search = search.query(q1)
        if description:
            search = search.query(q2)
        search.execute()
        result += search.to_queryset()

    return result

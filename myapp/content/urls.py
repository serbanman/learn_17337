from django.urls import path, re_path
from django.conf import settings

from content.views import VideoListViewSet, TagsListViewSet, CategoryListViewSet, VideoViewSet, \
    VideoCreateViewSet, VideoWatchViewSet, VideoRecommendedViewSet, VideoSearchViewSet

video_shards = f'[1-{settings.DATABASE_VIDEO_SHARDS_QUANTITY}]'

urlpatterns = [
    re_path(r'^videos/(?P<shard_id>' + video_shards + r'{1})/'
            r'(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            VideoViewSet.as_view()),
    re_path(r'^videos/watch/(?P<shard_id>' + video_shards + r'{1})/'
            r'(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            VideoWatchViewSet.as_view()),
    re_path(r'^videos/(?P<shard_id>' + video_shards + r'{1})/$', VideoListViewSet.as_view()),
    path('videos/recommended/', VideoRecommendedViewSet.as_view()),
    path('videos/create/', VideoCreateViewSet.as_view()),
    path('videos/search/', VideoSearchViewSet.as_view()),
    path('categories/', CategoryListViewSet.as_view()),
    path('tags/', TagsListViewSet.as_view())
]

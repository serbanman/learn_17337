from django.urls import path, re_path
from django.conf import settings

from content.views import VideoListViewSet, TagsListViewSet, CategoryListViewSet, VideoViewSet, \
    VideoCreateViewSet, VideoWatchViewSet, VideoRecommendedViewSet, VideoSearchViewSet, TestViewSet

video_shards = f'[1-{settings.DATABASE_VIDEO_SHARDS_QUANTITY}]'

urlpatterns = [
    re_path(r'^videos/(?P<shard_id>' + video_shards + r'{1})/'
            r'(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            VideoViewSet.as_view(), name='video_basic'),
    re_path(r'^videos/watch/(?P<shard_id>' + video_shards + r'{1})/'
            r'(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            VideoWatchViewSet.as_view(), name='video_watch'),
    re_path(r'^videos/(?P<shard_id>' + video_shards + r'{1})/$', VideoListViewSet.as_view(), name='video_list'),
    # path('videos/recommended/', VideoRecommendedViewSet.as_view(), name='video_recommended'),
    path('videos/recommended/', TestViewSet.as_view(), name='video_recommended'),
    path('videos/create/', VideoCreateViewSet.as_view(), name='video_create'),
    path('videos/search/', VideoSearchViewSet.as_view(), name='video_search'),
    path('categories/', CategoryListViewSet.as_view(), name='categories'),
    path('tags/', TagsListViewSet.as_view(), name='tags'),
    path('test/', TestViewSet.as_view(), name='tags'),
]

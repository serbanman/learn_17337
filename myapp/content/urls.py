from django.urls import path

from content.views import VideosListViewSet, TagsListViewSet, CategoryListViewSet

urlpatterns = [
    path('videos/', VideosListViewSet.as_view()),
    path('categories/', CategoryListViewSet.as_view()),
    path('tags/', TagsListViewSet.as_view())
]
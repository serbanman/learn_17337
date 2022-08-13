from rest_framework import viewsets, mixins, permissions, generics
from content.serializers import VideoSerializer, TagSerializer, CategorySerializer
from content.models import Video, Tag, Category


class VideosListViewSet(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.filter(shard_id=1)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class TagsListViewSet(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CategoryListViewSet(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

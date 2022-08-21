from rest_framework import mixins, permissions, generics
from rest_framework.response import Response

from content.serializers import VideoSerializer, TagSerializer, CategorySerializer
from content.models import Video, Tag, Category
from django.http import HttpResponse

from content.tasks import process_view, calculate_recommendations
from content.utils import RecommendationsService
from content.es_search import es_search
from django.core.cache import cache
from silk.profiling.profiler import silk_profile


class VideoCustomViewSet(generics.GenericAPIView):
    def get_object(self):
        shard_id = int(self.kwargs.get('shard_id'))
        video_id = self.kwargs.get('pk')
        obj = Video.objects.get(shard_id=shard_id, pk=video_id)
        return obj

    def get_queryset(self):
        shard_id = int(self.kwargs.get('shard_id'))
        obj = Video.objects.filter(shard_id=shard_id)
        return obj


def mixin_shard_call(func):
    """ Basically it is a get_or_404 function, but for custom get_object method """
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Video.DoesNotExist:
            return HttpResponse('Not found', status=404)
    return wrapper


class VideoViewSet(
    VideoCustomViewSet,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin
):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    @mixin_shard_call
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mixin_shard_call
    def put(self, request, *args, **kwargs):
        if 'category' in request.data.keys():
            request.data['category'] = kwargs['shard_id']
        return self.update(request, *args, **kwargs)

    @mixin_shard_call
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class VideoCreateViewSet(generics.GenericAPIView, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class VideoListViewSet(VideoCustomViewSet, mixins.ListModelMixin):
    """ list of all the videos """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class VideoWatchViewSet(VideoCustomViewSet):
    """ the same as main retrieve entrypoint, but with views counter and task scheduling"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    @mixin_shard_call
    def get(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        process_view.delay(user.id, instance.id, instance.category)
        calculate_recommendations.delay(user.id)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VideoRecommendedViewSet(generics.GenericAPIView, mixins.ListModelMixin):
    """ 10 recommended videos """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    def get_queryset(self):
        print(f'Cache is: {cache.get(self.request.user.id)}')
        cached = cache.get(self.request.user.id)
        if cached:
            print('Got from cache')
            return cached
        else:
            service = RecommendationsService(self.request.user.id)
            service.process()
            cache.set(self.request.user.id, service.result)
            return service.result

    @silk_profile(name='Recommendations GET')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class VideoSearchViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    def get_queryset(self):
        title = self.request.query_params.get("title")
        descr = self.request.query_params.get("description")

        key = f'{title if title else ""}__{descr if descr else ""}'
        cached = cache.get(key)
        if cached:
            print('Got from cache')
            return cached
        else:
            result = es_search(title, descr)
            cache.set(key, result)
            return result

    @silk_profile(name='Search GET')
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs:
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return Response(status=204)


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

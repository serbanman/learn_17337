from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.search import Search
from django_elasticsearch_dsl import Document
from content.models import Video
from django.conf import settings
from django.db.models import Case, When


class VideoSearch(Search):
    @property
    def _db(self):
        return self._index[0].split("__")[1]

    def to_queryset(self, keep_order=True):
        s = self

        if not hasattr(self, '_response'):
            s = self.source(excludes=['*'])
            s = s.execute()

        pks = [result.meta.id for result in s]
        # print(f'db: {self._db}')
        qs = Video.objects.using(self._db).filter(pk__in=pks)
        # print(f'qs: {qs}')
        if keep_order:
            preserved_order = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(pks)]
            )
            qs = qs.order_by(preserved_order)

        return qs


@registry.register_document
class VideoDocument(Document):
    class Index:
        name = 'video'

    class Django:
        model = Video
        fields = [
            'title',
            'description'
        ]

    def get_queryset(self):
        qs = Video.objects.none()
        shards = settings.DATABASE_VIDEO_SHARDS_QUANTITY
        for i in range(1, shards + 1):
            entries = Video.objects.chain_shard(i).all()
            # print(f'i -> {i}')
            qs |= entries
        return qs

    def _prepare_action(self, object_instance, action):
        data = {
            '_op_type': action,
            '_index': self._index._name + "__" + object_instance._state.db,
            '_id': object_instance.pk,
            '_source': (
                self.prepare(object_instance) if action != 'delete' else None
            ),
        }
        # print(f' >> from _prepare_action: {data}')
        return data

    @classmethod
    def search(cls, db=None, using=None, index=None):
        # db -> video_shard_%s
        # print(f'>>> from search: \nusing: {cls._get_using(using)}\n index: {("video__%s" % db) if db else cls._default_index(index)}\n doc_type: {[cls]}\n model: {cls.django.model}')
        return VideoSearch(
            using=cls._get_using(using),
            index=("video__%s" % db) if db else cls._default_index(index),
            doc_type=[cls],
            model=cls.django.model
        )


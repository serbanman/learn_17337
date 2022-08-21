from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from content.management.commands.create_content import Command as create_content
from content.models import Video
from django.core.cache import cache
from unittest.mock import Mock, patch
from django.conf import settings
from content.utils import RecommendationsService, generate_rec_cache_key

from users.models import History


class RecommendationsTests(APITestCase):
    databases = [
        'default',
        'video_shard_1',
        'video_shard_2',
        'video_shard_3',
        'video_shard_4',
        'video_shard_5',
        'history_shard_1',
        'history_shard_2',
        'history_shard_3',
    ]

    @classmethod
    def setUpTestData(cls):
        qs = Video.objects.chain_shard(1).all()
        print(f'>>>>QS: {qs}')
        if not qs.exists():
            create_content().handle()

    def setUp(self) -> None:
        self.user, _ = User.objects.get_or_create(username='test', password='test')
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        cache_key = generate_rec_cache_key(self.user.id)
        cache.set(cache_key, [])

    def test_cache_empty(self):
        cache_key = generate_rec_cache_key(self.user.id)
        cached_recs = cache.get(cache_key)
        self.assertFalse(cached_recs)
        print(f'>> test_cache_empty >> OK')

    def test_check_connection(self):
        rec_url = reverse('video_recommended')
        rec_resp = self.client.get(rec_url)
        self.assertEqual(rec_resp.status_code, status.HTTP_200_OK)
        print(f'>> test_check_connection >> OK')

    def test_is_data_type_list(self):
        rec_url = reverse('video_recommended')
        rec_resp = self.client.get(rec_url)
        data = rec_resp.data
        self.assertIsInstance(data, list)
        print(f'>> test_is_data_type_list >> OK')

    def test_is_returning_ten_entries(self):
        rec_url = reverse('video_recommended')
        rec_resp = self.client.get(rec_url)
        data = rec_resp.data
        self.assertEqual(len(data), 10)
        print(f'>> test_is_returning_ten_entries >> OK')

    def test_cache_exists(self):
        rec_url = reverse('video_recommended')
        self.client.get(rec_url)
        cache_key = generate_rec_cache_key(self.user.id)
        cached_recs = cache.get(cache_key)
        self.assertTrue(bool(cached_recs))
        print(f'>> test_cache_exists >> OK')

    def test_using_data_from_cache(self):
        rec_url = reverse('video_recommended')
        self.client.get(rec_url)

        with patch.object(RecommendationsService, 'process') as mock_obj:
            self.client.get(rec_url)

        mock_obj.assert_not_called()
        print(f'>> test_using_data_from_cache >> OK')

    def test_recommendations_change_after_watching(self):
        rec_url = reverse('video_recommended')
        first_resp = self.client.get(rec_url)
        first_data = first_resp.data
        video_to_watch = first_data[5]

        obj = History.objects.create(
            shard_id=self.user.id,
            user_id=self.user.id,
            video_id=f'{video_to_watch["category"]}__{video_to_watch["id"]}'
        )
        cache_key = generate_rec_cache_key(self.user.id)
        cache.set(cache_key, [])
        second_resp = self.client.get(rec_url)
        second_data = second_resp.data

        self.assertNotEqual(first_data, second_data)
        obj.delete()
        print(f'>> test_recommendations_change_after_watching >> OK')

    def test_watched_video_not_in_recs(self):
        rec_url = reverse('video_recommended')
        first_resp = self.client.get(rec_url)
        first_data = first_resp.data
        watched_ids = []
        history_objs = []
        for el in first_data:
            history_objs.append(
                History.objects.create(
                    shard_id=self.user.id,
                    user_id=self.user.id,
                    video_id=f'{el["category"]}__{el["id"]}'
                )
            )
            watched_ids.append(el["r_id"])

        cache_key = generate_rec_cache_key(self.user.id)
        cache.set(cache_key, [])
        second_resp = self.client.get(rec_url)
        second_data = second_resp.data

        for el in second_data:
            self.assertNotIn(el['r_id'], watched_ids)
        for obj in history_objs:
            obj.delete()
        print(f'>> test_watched_video_not_in_recs >> OK')

    def test_recs_exist_if_all_videos_watched(self):
        history_objs = []
        for i in range(1, settings.DATABASE_VIDEO_SHARDS_QUANTITY + 1):
            video_qs = Video.objects.chain_shard(i).all()
            for video in video_qs:
                history_objs.append(
                    History.objects.create(
                        shard_id=self.user.id,
                        user_id=self.user.id,
                        video_id=f'{video.category}__{video.id}'
                    )
                )
        rec_url = reverse('video_recommended')
        resp = self.client.get(rec_url)
        data = resp.data

        self.assertTrue(bool(data))
        self.assertEqual(len(data), 10)

        for obj in history_objs:
            obj.delete()
        print(f'>> test_recs_exist_if_all_videos_watched >> OK')

    def test_is_more_viewed_in_default_recs(self):
        videos_changed = []
        r_ids = []
        for i in range(1, settings.DATABASE_VIDEO_SHARDS_QUANTITY + 1):
            video_qs = Video.objects.chain_shard(i).all()[:2]
            for video in video_qs:
                video.unique_views += 1
                video.save()
                videos_changed.append(video)
                r_ids.append(video.r_id)

        rec_url = reverse('video_recommended')
        resp = self.client.get(rec_url)
        data = resp.data

        for el in data:
            self.assertIn(el['r_id'], r_ids)

        for obj in videos_changed:
            obj.unique_views = 0
            obj.save()
        print(f'>> test_is_more_viewed_in_default_recs >> OK')

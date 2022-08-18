from django.contrib.auth.models import User
from content.models import Video, Category, Tag
from users.models import History
import uuid
import math


class HistoryService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = self._get_user_instance()

        self.user_history = self._get_user_history()

    def _get_user_instance(self):
        return User.objects.get(id=self.user_id)

    def _get_user_history(self):
        return History.objects.filter(shard_id=self.user.id, user_id=self.user.id)


class ViewsService(HistoryService):
    def __init__(self, user_id: int, video_id: uuid.UUID, category_id: int):
        super().__init__(user_id)
        self.video_id = video_id
        self.category_id = category_id
        self.video = self._get_video_instance()

    def _get_video_instance(self):
        video = Video.objects.get(shard_id=self.category_id, id=self.video_id)
        return video

    def _increase_total_views(self):
        self.video.total_views += 1

    def _increase_unique_views(self):
        self.video.unique_views += 1

    def _check_if_viewed(self):
        qs = self.user_history.filter(video_id__endswith=self.video.id)
        return qs.exists()

    def _create_history_entry(self):
        new_video_id = f'{self.video.category}__{self.video.id}'
        History.objects.create(shard_id=self.user.id, user_id=self.user.id, video_id=new_video_id)

    def process_view(self):
        self._increase_total_views()
        if not self._check_if_viewed():
            self._increase_unique_views()
            self._create_history_entry()

        self.video.save()


class RecommendationsService(HistoryService):
    QUANTITY = 10

    def __init__(self, user_id):
        super().__init__(user_id)
        self.arranged_tags = self._get_distribution()

        self.__result = []
        self.history_video_ids = self._get_history_video_id_array()


    @property
    def result(self):
        return self.__result

    def _get_history_video_id_array(self):
        return list(x.video_id.split('__')[1] for x in self.user_history)

    def _get_distribution(self):
        tags = {}
        tags_count = 0
        arranged_tags = []

        history_entries = {}
        for el in self.user_history:
            category_id, video_id = el.video_id.split('__')
            category_id = int(category_id)
            if category_id not in history_entries.keys():
                history_entries[category_id] = []
            history_entries[category_id].append(video_id)

        for category_id in history_entries.keys():
            videos = Video.objects.filter(shard_id=category_id, id__in=history_entries[category_id])
            for video in videos:
                for tag_id in video.tags:
                    if tag_id not in tags.keys():
                        tags[tag_id] = 1
                    else:
                        tags[tag_id] += 1
                    tags_count += 1

        # for el in self.user_history:
        #     category_id, video_id = el.video_id.split('__')
        #     video_inst = Video.objects.get(shard_id=int(category_id), id=video_id)
        #     for tag_id in video_inst.tags:
        #         if tag_id not in tags.keys():
        #             tags[tag_id] = 1
        #         else:
        #             tags[tag_id] += 1
        #         tags_count += 1

        temp_dict = tags.copy()

        def iter_arrange(dict_copy):
            if not dict_copy:
                return
            max_num = 0
            max_el = None

            for tag in dict_copy.keys():
                if tags[tag] > max_num:
                    max_num = tags[tag]
                    max_el = tag

            arranged_tags.append([max_el, dict_copy[max_el] / tags_count])
            dict_copy.pop(max_el)
            return iter_arrange(dict_copy)

        iter_arrange(temp_dict)

        print(f' Tags: {tags}')
        # print(f' Arranged tags: {arranged_tags}')
        return arranged_tags

    def _get_category_by_tag_id(self, tag_id):
        tag = Tag.objects.select_related('category').get(id=tag_id)
        return tag.category

    def _instantiate_arranged_tags(self, arranged_tags):
        tags = [el[0] for el in arranged_tags]

        tags_inst = Tag.objects.select_related('category').filter(id__in=tags)
        print(tags, tags_inst)

        inst_array = []
        for tag_id, distribution in arranged_tags:
            for tag in tags_inst:
                if tag.id == tag_id:
                    inst_array.append([tag, distribution])
                    continue
        print('before', arranged_tags)
        print('after', inst_array)

    def _get_top_videos_by_tag(self, tag_id: int, quantity: int):
        array = []
        counter = 0
        category = self._get_category_by_tag_id(tag_id)
        videos = Video.objects.filter(shard_id=category.id, tags__contains=tag_id).order_by('-unique_views')
        for video in videos:
            if counter >= quantity:
                break
            if video not in self.__result and str(video.id) not in self.history_video_ids:
                array.append(video)
                counter += 1
        return array

    def _get_default_recommendations(self):
        # TODO: better shard management
        for i in range(1, 6):
            videos = Video.objects.filter(shard_id=i).order_by('-unique_views')[:2]
            self.__result += videos

    def process(self):
        # print(f'Init length: {len(self.__result)}')
        # print(f' History video ids {self.history_video_ids}')
        self._instantiate_arranged_tags(self.arranged_tags)
        if self.user_history.exists():
            for el in self.arranged_tags:
                if len(self.__result) == self.QUANTITY:
                    print(self.__result)
                    return

                q_of_tag = math.ceil(el[1] * self.QUANTITY)
                tag_id = el[0]
                videos = self._get_top_videos_by_tag(tag_id, q_of_tag)

                if len(self.__result) + len(videos) <= self.QUANTITY:
                    self.__result += videos
                else:
                    margin = self.QUANTITY - len(self.__result)
                    self.__result += videos[:margin]
        else:
            self._get_default_recommendations()

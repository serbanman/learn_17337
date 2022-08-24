from .database import sessions
from .config import VIDEO_SHARD_KEY, VIDEO_SHARDS_QUANTITY, HISTORY_SHARD_KEY
from .models import History, Video, Tag
from .utils import ConnectionManager
import math


class HistoryService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.sessions = sessions
        self.user_shard = self._get_shard_name()
        self.user_history = self._get_user_history()

    def _get_shard_id(self):
        return self.user_id % 3 + 1

    def _get_shard_name(self):
        return HISTORY_SHARD_KEY % self._get_shard_id()

    def _get_history_session(self):
        return self.sessions[self.user_shard]

    def _get_user_history(self):
        with ConnectionManager(self.user_shard) as con:
            result = con.query(History).filter(History.user_id == self.user_id).all()

        return result


class RecommendationsService(HistoryService):
    """
    Methods may look confusing, but I managed to reduce amount of db transactions from 51 to 18 on 7 shards
    """

    QUANTITY = 10

    def __init__(self, user_id):
        super().__init__(user_id)
        self.__result = []

    @property
    def result(self):
        return self.__result

    @property
    def result_ids(self):
        return list(entry.id for entry in self.__result)

    @staticmethod
    def _get_video_shard_name(number):
        return VIDEO_SHARD_KEY % number

    def _get_history_video_id_array(self):
        return list(entry.video_id.split('__')[1] for entry in self.user_history)

    def _get_distribution(self):
        tags = {}
        tags_count = 0
        arranged_tags = []

        history_entries = {}
        """ Distributing videos from history by category, so we can fetch them from one shard at once """
        for el in self.user_history:
            category_id, video_id = el.video_id.split('__')
            category_id = int(category_id)
            if category_id not in history_entries.keys():
                history_entries[category_id] = []
            history_entries[category_id].append(video_id)

        """ Counting the tags from every video watched """
        for category_id in history_entries.keys():
            shard_name = self._get_video_shard_name(category_id)
            with ConnectionManager(shard_name) as con:
                videos = con.query(Video).filter(Video.id.in_(history_entries[category_id])).all()
            for video in videos:
                for tag_id in video.tags:
                    if tag_id not in tags.keys():
                        tags[tag_id] = 1
                    else:
                        tags[tag_id] += 1
                    tags_count += 1

        """ Creating [[tag_id, tag_weight],] list """
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

        # print(f' Tags: {tags}')
        # print(f' Arranged tags: {arranged_tags}')
        return arranged_tags

    @staticmethod
    def _instantiate_arranged_tags(arranged_tags):
        """
        Changing the [[tag_id, tag_weight],] to [[Tag, tag_weight],], so we can access Tag table only once
        """
        tags_id_list = [el[0] for el in arranged_tags]
        with ConnectionManager('default_db') as con:
            tags_instances = con.query(Tag).filter(Tag.id.in_(tags_id_list)).all()
        inst_array = []
        for tag_id, distribution in arranged_tags:
            for tag in tags_instances:
                if tag.id == tag_id:
                    inst_array.append([tag, distribution])
                    continue
        return inst_array

    def _get_top_videos_by_tag(self, tag, quantity: int):
        """
        Retrieving top N videos by unique_views by Tag
        """
        array = []
        counter = 0
        history_video_ids = self._get_history_video_id_array()
        with ConnectionManager(self._get_video_shard_name(tag.category_id)) as con:
            videos = con.query(Video).filter(Video.tags.contains([tag.id])).order_by(-Video.unique_views).all()
        for video in videos:
            if counter >= quantity:
                break
            """
            Since videos can have more than 1 tag,
            we should check that the video is not already picked or had been seen
            """
            if video.id not in self.result_ids and str(video.id) not in history_video_ids:
                array.append(video)
                counter += 1
        return array

    def _get_default_recommendations(self):
        """ Get recommendations for user with no history or insufficient views for 10 recommended videos """
        # TODO: better default logic
        for i in range(1, VIDEO_SHARDS_QUANTITY + 1):
            shard_name = self._get_video_shard_name(i)
            with ConnectionManager(shard_name) as con:
                result = con.query(Video).order_by(-Video.unique_views)[:2]
            for video in result:
                if len(self.__result) < 10:
                    self.__result.append(video)
                else:
                    break

    def process(self):
        if self.user_history:
            arranged_tags = self._get_distribution()
            instantiated_arranged_tags = self._instantiate_arranged_tags(arranged_tags)
            for el in instantiated_arranged_tags:
                if len(self.__result) == self.QUANTITY:
                    # print(self.__result)
                    return

                q_of_tag = math.ceil(el[1] * self.QUANTITY)
                tag = el[0]
                videos = self._get_top_videos_by_tag(tag, q_of_tag)

                """ Slice videos array to get exactly 10 entries """
                if len(self.__result) + len(videos) <= self.QUANTITY:
                    self.__result += videos
                else:
                    margin = self.QUANTITY - len(self.__result)
                    self.__result += videos[:margin]

            if len(self.__result) < 10:
                self._get_default_recommendations()
        else:
            self._get_default_recommendations()
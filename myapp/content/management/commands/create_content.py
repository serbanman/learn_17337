from django.core.management.base import BaseCommand
from content.models import Tag, Category, Video
import random
from random_word import RandomWords

class Command(BaseCommand):
    def handle(self, *args, **options):
        category_names = ["Кулинария", "Спорт", "Природа", "Политика", "Обучение"]

        tags_list = [
            ["Мясо", "Рыба", "Овощи", "Напитки", "Французская кухня", "Итальянская кухня"],
            ["Футбол", "Баскетбол", "ММА", "Формула-1", "Зимний спорт", "Киберспорт"],
            ["Рыбалка", "Походы", "Документальные", "Сплав", "Животные", "Космос"],
            ["Теории заговора", "История", "Войны", "Выборы", "Интервью", "Новости"],
            ["Айти", "Языки", "Рукоделие", "Личностный рост", "Школа", "Математика"]
        ]
        r = RandomWords()
        random_words = r.get_random_words()
        for ind, category in enumerate(category_names):
            print('Creating Category')
            category_obj = Category.objects.create(name=category)
            print(f'Success, id {category_obj.id}')
            tags = tags_list[ind]
            category_tags = []
            for tag in tags:
                print('Creating tags')
                new_tag_obj = Tag.objects.create(name=tag, category=category_obj)
                print(f'Success, id {new_tag_obj.id}')
                category_tags.append(new_tag_obj)

            for i in range(1, 11):
                print('Creating video')
                # random_words = r.get_random_words()
                if isinstance(random_words, list):
                    video_tags = random.sample(category_tags, random.randint(1, 3))
                    obj = Video.objects.create(
                        shard_id=category_obj.id,
                        title=' '.join(list(tag.name for tag in video_tags)) + f' No.{i}',
                        description=' '.join(random.sample(random_words, random.randint(2, 5))),
                        category=category_obj.id,
                        tags=list(tag.id for tag in video_tags)
                    )
                    print(f'Success, video id {obj.id}')

            category_tags = []



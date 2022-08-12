from django.db import models


class Tag(models.Model):
    id = models.IntegerField(primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ManyToManyField('Category', related_name='tags')

    def __str__(self):
        return f'{self.id}, {self.name}, {self.category}'

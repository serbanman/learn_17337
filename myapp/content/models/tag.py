from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ForeignKey('Category', related_name='tags', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.id}, {self.name}, {self.category}'

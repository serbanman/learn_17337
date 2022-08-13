from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f'{self.id}, {self.name}'


# Generated by Django 4.1 on 2022-08-11 16:38

import content.models.video
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('r_id', models.CharField(default=content.models.video.get_r_id, max_length=10, unique=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('total_views', models.IntegerField(default=0)),
                ('unique_views', models.IntegerField(default=0)),
                ('category', models.CharField(blank=True, max_length=255, null=True)),
                ('tags', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('category', models.ManyToManyField(related_name='tags', to='content.category')),
            ],
        ),
    ]
from rest_framework import serializers
from content.models import Video, Tag, Category


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

    def create(self, validated_data):
        category_id = validated_data.get('category')
        return Video.objects.create(shard_id=category_id, **validated_data)

    def validate(self, attrs):
        if "category" not in attrs.keys():
            raise serializers.ValidationError("Category is required")
        return super().validate(attrs)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

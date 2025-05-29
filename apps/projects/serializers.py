from rest_framework import serializers
from .models import Project, Technology, Comment, Like, ProjectMedia
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from apps.users.serializers import UserSerializer # Чтобы видеть информацию о пользователе


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'slug']


class ProjectMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMedia
        fields = ['id', 'project', 'file', 'file_type', 'caption', 'uploaded_at']
        read_only_fields = ['project'] # Устанавливается во view при создании


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    # owner = UserSerializer(read_only=True) # Показывает детальную информацию об авторе (только для чтения)
    owner_username = serializers.ReadOnlyField(source='owner.username') # Проще - только имя пользователя
    owner_id = serializers.ReadOnlyField(source='owner.id')
    
    tags = TagListSerializerField() # От django-taggit-serializer
    technologies = TechnologySerializer(many=True, read_only=True) # Для отображения
    technology_ids = serializers.PrimaryKeyRelatedField(
        queryset=Technology.objects.all(), source='technologies', many=True, write_only=True, required=False
    )
    
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    
    # Если хотим показать вложенные media_files при чтении
    # media_files = ProjectMediaSerializer(many=True, read_only=True) 

    class Meta:
        model = Project
        fields = [
            'id', 'slug', 'title', 'description', 'main_image', 'project_url', 'repository_url',
            'owner_username', 'owner_id', 'tags', 'technologies', 'technology_ids',
            'created_at', 'updated_at', 'comments_count', 'likes_count'
            # 'media_files'
        ]
        read_only_fields = ('slug', 'owner_username', 'owner_id', 'created_at', 'updated_at', 'comments_count', 'likes_count')
        # `main_image` не будет required при PATCH, но required при POST (DRF по умолчанию так и делает)

    def create(self, validated_data):
        # Убедимся, что 'technologies' корректно обработан (из technology_ids)
        if 'technologies' in validated_data:
            technologies_data = validated_data.pop('technologies') # Из source='technologies'
            project = super().create(validated_data)
            project.technologies.set(technologies_data)
        else:
            project = super().create(validated_data)
        return project

    def update(self, instance, validated_data):
        if 'technologies' in validated_data:
            technologies_data = validated_data.pop('technologies')
            instance = super().update(instance, validated_data)
            instance.technologies.set(technologies_data)
        else: # если technology_ids не переданы, но technologies там было
            instance = super().update(instance, validated_data)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'project', 'author_username', 'text', 'created_at', 'updated_at']
        read_only_fields = ['author_username', 'project', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'project', 'user_username', 'created_at']
        read_only_fields = ['user_username', 'project', 'created_at']

    def validate(self, data):
        # Проверяем, что лайк ставится текущим пользователем для указанного проекта
        # project должен быть в context от view
        request = self.context.get('request')
        project = self.context.get('project')
        if Like.objects.filter(project=project, user=request.user).exists():
            raise serializers.ValidationError("You have already liked this project.")
        return data
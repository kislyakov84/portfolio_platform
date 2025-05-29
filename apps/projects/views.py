from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Technology, Comment, Like, ProjectMedia
from .serializers import (
    ProjectSerializer, TechnologySerializer, CommentSerializer, LikeSerializer, ProjectMediaSerializer
)
from .permissions import IsOwnerOrReadOnly # Кастомное разрешение

# Поиск с использованием Q-объектов, если Haystack покажется излишним
from django.db.models import Q

class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # Можно добавить фильтрацию по имени и пагинацию если нужно


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related('tags', 'technologies', 'owner', 'comments', 'likes')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly] # IsOwnerOrReadOnly для update/delete
    lookup_field = 'slug' # Использовать slug вместо pk для деталей проекта
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'technologies__slug', 'owner__username'] # Фильтрация по тегам, технологиям, автору
    search_fields = ['title', 'description', 'tags__name', 'technologies__name'] # Поиск по тексту
    ordering_fields = ['created_at', 'likes_count', 'comments_count', 'title'] # Сортировка
    ordering = ['-created_at'] # Сортировка по умолчанию

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) # При создании проекта, автор - текущий пользователь
    
    # Для загрузки нескольких медиа-файлов (ProjectMedia)
    # /api/projects/{slug}/media_files/
    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAuthenticatedOrReadOnly]) # IsOwnerOrReadOnly?
    def media_files(self, request, slug=None):
        project = self.get_object()
        if request.method == 'POST':
            if project.owner != request.user and not request.user.is_staff:
                 return Response(
                    {"detail": "You do not have permission to perform this action."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Можно обрабатывать request.FILES.getlist('file_field_name') для множественной загрузки
            # или ожидать один файл за раз
            serializer = ProjectMediaSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # GET
        media = ProjectMedia.objects.filter(project=project)
        serializer = ProjectMediaSerializer(media, many=True, context={'request': request})
        return Response(serializer.data)

    # /api/projects/{slug}/like/
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        project = self.get_object()
        user = request.user

        if request.method == 'POST':
            if Like.objects.filter(project=project, user=user).exists():
                return Response({'detail': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
            Like.objects.create(project=project, user=user)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            like_instance = Like.objects.filter(project=project, user=user).first()
            if not like_instance:
                return Response({'detail': 'Not liked yet.'}, status=status.HTTP_400_BAD_REQUEST)
            like_instance.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

# Представления для комментариев лучше делать вложенными в проекты или как отдельные списки
# Например, /api/projects/{project_slug}/comments/
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Фильтруем комментарии по slug проекта из URL
        project_slug = self.kwargs['project_slug']
        return Comment.objects.filter(project__slug=project_slug)

    def perform_create(self, serializer):
        project_slug = self.kwargs['project_slug']
        project = Project.objects.get(slug=project_slug)
        serializer.save(author=self.request.user, project=project)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly] # Автор комментария может его менять/удалять
    lookup_url_kwarg = 'comment_pk' # Имя параметра в URL для pk комментария

    def get_queryset(self):
        project_slug = self.kwargs['project_slug']
        return Comment.objects.filter(project__slug=project_slug)
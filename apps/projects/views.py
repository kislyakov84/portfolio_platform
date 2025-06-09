# Файл: apps/projects/views.py

# Убираем неиспользуемый импорт Any
# from typing import Any
from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Technology, Comment, Like, ProjectMedia
from .serializers import (
    ProjectSerializer,
    TechnologySerializer,
    CommentSerializer,
    ProjectMediaSerializer,
)
from .permissions import IsOwnerOrReadOnly


class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related(
        "tags", "technologies", "owner", "comments", "likes"
    )
    serializer_class = ProjectSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    lookup_field = "slug"

    # Из-за несовершенства в django-stubs, Pylance выдает ошибку о несовместимости типов.
    # Так как проблема не в нашем коде, а во внешних определениях, мы осознанно
    # подавляем эту ошибку для данной конкретной строки.
    filter_backends = (  # type: ignore
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        "tags__name",
        "technologies__slug",
        "owner__username",
    )
    search_fields = (
        "title",
        "description",
        "tags__name",
        "technologies__name",
    )
    ordering_fields = (
        "created_at",
        "likes_count",
        "comments_count",
        "title",
    )
    ordering = ("-created_at",)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Мы ранее исправляли этот экшен, но теперь, после фиксов моделей, он окончательно корректен
    # permission_classes здесь был `[IsAuthenticatedOrReadOnly]` и ручная проверка, исправим на IsOwnerOrReadOnly
    @action(
        detail=True, methods=["post", "get"], permission_classes=[IsOwnerOrReadOnly]
    )
    def media_files(self, request, slug=None):
        project = self.get_object()
        if request.method == "POST":
            # Ручная проверка больше не нужна, IsOwnerOrReadOnly сделает это за нас для небезопасных методов
            # if project.owner != request.user and not request.user.is_staff:
            #      return Response(
            #         {"detail": "You do not have permission to perform this action."},
            #         status=status.HTTP_403_FORBIDDEN
            #     )

            serializer = ProjectMediaSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # GET
        media = ProjectMedia.objects.filter(project=project)
        serializer = ProjectMediaSerializer(
            media, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        project = self.get_object()
        user = request.user

        like_instance, created = Like.objects.get_or_create(project=project, user=user)

        if created:
            return Response(
                {"status": "liked", "likes_count": project.likes.count()},
                status=status.HTTP_201_CREATED,
            )
        else:
            like_instance.delete()
            # Важный момент: нельзя возвращать тело ответа со статусом 204. Это нарушает стандарт HTTP.
            # Поэтому likes_count здесь возвращать не нужно.
            return Response(status=status.HTTP_204_NO_CONTENT)


# ... (CommentListCreateView и CommentDetailView без изменений)
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        project_slug = self.kwargs["project_slug"]
        return Comment.objects.filter(project__slug=project_slug)

    def perform_create(self, serializer):
        project_slug = self.kwargs["project_slug"]
        project = Project.objects.get(slug=project_slug)
        serializer.save(author=self.request.user, project=project)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    lookup_url_kwarg = "comment_pk"

    def get_queryset(self):
        project_slug = self.kwargs["project_slug"]
        return Comment.objects.filter(project__slug=project_slug)

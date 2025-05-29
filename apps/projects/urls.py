from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TechnologyViewSet, CommentListCreateView, CommentDetailView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'technologies', TechnologyViewSet, basename='technology')

urlpatterns = [
    path('', include(router.urls)),
    # Вложенные маршруты для комментариев
    path('projects/<slug:project_slug>/comments/', CommentListCreateView.as_view(), name='project-comments-list-create'),
    path('projects/<slug:project_slug>/comments/<int:comment_pk>/', CommentDetailView.as_view(), name='project-comment-detail'),
]
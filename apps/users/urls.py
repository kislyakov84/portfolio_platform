from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView, CurrentUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') # /api/users/ , /api/users/<pk>/

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Получение токена
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Обновление токена
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),   # Верификация токена
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
]
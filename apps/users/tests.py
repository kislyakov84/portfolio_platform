# Файл: apps/users/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Убираем неиспользуемый импорт APIClient - ошибка Ruff F401 будет исправлена
# from rest_framework.test import APIClient
# Убираем get_user_model
# from django.contrib.auth import get_user_model
# Импортируем нашу конкретную модель пользователя
from .models import CustomUser

# Теперь User - это наш CustomUser, и Pylance это знает
User = CustomUser


class UserAuthTests(APITestCase):

    def setUp(self):
        # Код без изменений...
        self.register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.login_data_username = {
            "username": "testuser",
            "password": "testpassword123",
        }
        self.login_url = reverse("token_obtain_pair")
        self.register_url = reverse("auth_register")
        self.current_user_url = reverse("current_user")

    def test_user_registration_success(self):
        """Проверка успешной регистрации пользователя."""
        response = self.client.post(
            self.register_url, self.register_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        # Pylance больше не будет ругаться, т.к. он знает, что у CustomUser есть поле username
        self.assertEqual(User.objects.get().username, "testuser")

    # ... остальная часть файла остается без изменений,
    # так как проблема была только в строке выше.
    # Но для чистоты привожу полный код класса.

    def test_user_registration_password_mismatch(self):
        """Проверка ошибки при несовпадении паролей."""
        data = self.register_data.copy()
        data["password2"] = "wrongpassword"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # После установки djangorestframework-stubs, здесь ошибки не будет
        self.assertIn("password", response.data)

    def test_user_registration_duplicate_email(self):
        """Проверка ошибки при дублировании email."""
        User.objects.create_user(
            username="anotheruser",
            email=self.register_data["email"],
            password="password",
        )
        response = self.client.post(
            self.register_url, self.register_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_login_and_get_current_user(self):
        """Проверка логина, получения токенов и данных о текущем пользователе."""
        User.objects.create_user(**self.register_data)

        response = self.client.post(
            self.login_url, self.login_data_username, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        access_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.register_data["username"])

    def test_update_current_user(self):
        """Проверка обновления данных пользователя."""
        # Исправим зависимость тестов друг от друга - это лучшая практика

        # Строка 'user = User.objects.create_user(...)' изменена на:
        # Просто создаем пользователя, его возвращаемое значение нам не нужно.
        User.objects.create_user(
            username="updateme", password="password123", email="updateme@test.com"
        )
        self.client.login(username="updateme", password="password123")

        update_data = {"first_name": "Updated", "bio": "A new bio."}
        response = self.client.patch(self.current_user_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # После установки djangorestframework-stubs, здесь ошибки нет
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["bio"], "A new bio.")

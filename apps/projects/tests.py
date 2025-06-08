# Файл: apps/projects/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


from apps.users.models import CustomUser
from .models import Project, Comment

# Явно указываем, что User - это наш CustomUser
User = CustomUser


class ProjectAPITests(APITestCase):
    def setUp(self):
        # Создаем двух пользователей
        # Теперь Pylance не будет ругаться, так как знает, что у CustomUser.objects есть метод create_user
        self.user1 = User.objects.create_user(
            username="user1", password="password123", email="user1@test.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password123", email="user2@test.com"
        )

        # Логиним первого пользователя
        self.client.login(username="user1", password="password123")

        # Создаем проект от имени user1
        self.project1 = Project.objects.create(
            owner=self.user1,
            title="Test Project 1",
            description="A description for the test project.",
        )

        self.project_list_url = reverse("project-list")
        self.project_detail_url = reverse(
            "project-detail", kwargs={"slug": self.project1.slug}
        )

    # Остальные тесты не требуют изменений, так как они не обращаются
    # к специфичным методам модели User.
    # Но убедимся, что после рефакторинга like endpoint'а тесты соответствуют новой логике.

    # ... (тесты create, update, delete, comments остаются прежними)

    def test_create_project_authenticated(self):
        """Проверка создания проекта авторизованным пользователем."""
        url = reverse("project-list")
        data = {
            "title": "New Awesome Project",
            "description": "More description.",
            "tags": "test,api",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.latest("id").owner, self.user1)

    def test_create_project_unauthenticated(self):
        """Проверка запрета на создание проекта неавторизованным пользователем."""
        self.client.logout()
        url = reverse("project-list")
        data = {"title": "Anonymous Project", "description": "Should not be created."}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_by_owner(self):
        """Проверка обновления проекта его владельцем."""
        data = {"title": "Updated Title"}
        response = self.client.patch(self.project_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.title, "Updated Title")

    def test_update_project_by_non_owner(self):
        """Проверка запрета на обновление проекта не владельцем."""
        self.client.login(username="user2", password="password123")
        data = {"title": "Malicious Update"}
        response = self.client.patch(self.project_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_by_owner(self):
        """Проверка удаления проекта его владельцем."""
        response = self.client.delete(self.project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project1.pk).exists())

    def test_add_comment_to_project(self):
        """Проверка добавления комментария к проекту."""
        url = reverse(
            "project-comments-list-create", kwargs={"project_slug": self.project1.slug}
        )
        data = {"text": "This is a test comment."}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().author, self.user1)

    def test_like_unlike_project_toggle(self):
        """Проверка лайка и анлайка проекта по логике 'toggle'."""
        url = reverse("project-like", kwargs={"slug": self.project1.slug})

        self.client.login(username="user2", password="password123")

        # Ставим лайк
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Теперь Pylance не ругается на эту строку!
        self.assertEqual(self.project1.likes.count(), 1)
        self.assertEqual(response.data["status"], "liked")

        # Убираем лайк (тем же запросом)
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # И на эту тоже.
        self.assertEqual(self.project1.likes.count(), 0)

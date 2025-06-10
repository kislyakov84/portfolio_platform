from django.db import models  # models.Manager будет доступен через models
from django.conf import settings
from taggit.managers import TaggableManager
from django.utils.text import slugify


def project_main_image_upload_path(instance, filename):  # Переименовал для ясности
    return f"projects/{instance.slug}/images/main/{filename}"  # Добавил /main/ для основного


def project_media_upload_path(instance, filename):
    # instance здесь это ProjectMedia, поэтому instance.project.slug
    return f"projects/{instance.project.slug}/media/{instance.file_type}/{filename}"


class Technology(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Убедимся, что даже если slug задан, он корректен (на случай прямого присвоения)
        # В данном случае, если задан, то доверяем. Если нет, то генерируем.
        # Для уникальности при генерации, если потребуется, можно добавить логику как в Project.
        super().save(*args, **kwargs)  # Вызываем super() один раз в конце

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Technologies"


class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    main_image = models.ImageField(
        upload_to=project_main_image_upload_path,  # Используем новую функцию
        null=True,
        blank=True,
    )
    project_url = models.URLField(blank=True, null=True)
    repository_url = models.URLField(blank=True, null=True)

    technologies = models.ManyToManyField(
        Technology, related_name="projects", blank=True
    )
    tags = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes: "models.Manager[Like]"
    comments: "models.Manager[Comment]"
    media_files: "models.Manager[ProjectMedia]"

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерируем слаг только если он не предоставлен
            base_slug = slugify(self.title)
            # Если слаг пустой после slugify (например, название было "---"), генерируем что-то
            if not base_slug:
                import uuid

                base_slug = str(uuid.uuid4())[:8]  # Короткий UUID как крайний случай

            slug_candidate = base_slug
            counter = 1
            # Проверяем существование слагов, исключая текущий объект, если он уже сохранен (при обновлении)
            qs_filter = {"slug__iexact": slug_candidate}
            # Используем self._state.adding чтобы понять, создается ли новый объект
            if not self._state.adding and self.pk is not None:
                qs = Project.objects.filter(**qs_filter).exclude(pk=self.pk)
            else:
                qs = Project.objects.filter(**qs_filter)

            while qs.exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
                # Обновляем фильтр для следующей итерации
                qs_filter["slug__iexact"] = slug_candidate
                if not self._state.adding and self.pk is not None:
                    qs = Project.objects.filter(**qs_filter).exclude(pk=self.pk)
                else:
                    qs = Project.objects.filter(**qs_filter)
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class ProjectMedia(models.Model):
    FILE_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("archive", "Archive"),
        ("other", "Other"),
    ]
    project = models.ForeignKey(
        Project, related_name="media_files", on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to=project_media_upload_path  # Используем новую функцию
    )
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default="image")
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caption or self.file_type} for {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.project}"

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Like by {self.user} on {self.project}"

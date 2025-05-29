from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager # Для поля tags

def project_image_upload_path(instance, filename):
    return f'projects/{instance.slug}/images/{filename}'

def project_video_upload_path(instance, filename):
    return f'projects/{instance.slug}/videos/{filename}'

class Technology(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Technologies"

class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True) # Будет генерироваться из title
    description = models.TextField()
    # Скриншот или лого проекта (главное изображение)
    main_image = models.ImageField(upload_to=project_image_upload_path, null=True, blank=True)
    project_url = models.URLField(blank=True, null=True) # Ссылка на живой проект
    repository_url = models.URLField(blank=True, null=True) # Ссылка на репозиторий
    
    technologies = models.ManyToManyField(Technology, related_name='projects', blank=True)
    tags = TaggableManager(blank=True) # Используем django-taggit

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            # Базовая генерация слага, можно добавить уникальность, если нужно
            self.slug = slugify(self.title)
            # Проверка на уникальность и добавление суффикса если уже существует
            original_slug = self.slug
            queryset = Project.objects.filter(slug__iexact=original_slug).exclude(pk=self.pk)
            counter = 1
            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                queryset = Project.objects.filter(slug__iexact=self.slug).exclude(pk=self.pk)
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

# Пример для других медиафайлов проекта (если надо несколько изображений/видео на проект)
class ProjectMedia(models.Model):
    FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('archive', 'Archive'), # e.g. zip, rar
        ('other', 'Other'),
    ]
    project = models.ForeignKey(Project, related_name='media_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='projects/media_files/') # Путь можно детализировать
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default='image')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} for {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.project}'

    class Meta:
        ordering = ['-created_at']


class Like(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user') # Пользователь может лайкнуть проект только один раз
        ordering = ['-created_at']

    def __str__(self):
        return f'Like by {self.user} on {self.project}'
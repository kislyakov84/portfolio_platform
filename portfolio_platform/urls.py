from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from drf_yasg.views import get_schema_view # Опционально, для drf-yasg
# from drf_yasg import openapi              # Опционально, для drf-yasg
# from rest_framework import permissions    # Опционально, для drf-yasg

# schema_view = get_schema_view(   # Опционально
#    openapi.Info(
#       title="Portfolio Platform API",
#       default_version='v1',
#       description="API for showcasing personal projects",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@example.com"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.projects.urls')),
    # path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), # Опционально Swagger
    # path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),        # Опционально ReDoc
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Для разработки
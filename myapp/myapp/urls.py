from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import authentication, permissions
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


schema_view = get_schema_view(
    openapi.Info(
        title='TEST API',
        default_version='v1',
        description='test description',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(authentication.SessionAuthentication,)
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("silk/", include("silk.urls", namespace="silk")),
    path('content/', include('content.urls')),
    # path('/users', include('users.urls')),
]

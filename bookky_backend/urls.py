"""bookky_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_url_patterns = [ 
    path('v1/', include('bookky.urls')), 
    ]
schema_view = get_schema_view( 
    openapi.Info( 
        title="Bookky API",
        description= "API for Bookky service" ,
        default_version='v1', 
        terms_of_service="https://www.google.com/policies/terms/",
        contact = openapi.Contact(email="bookkymaster@bookky.org"),
        license = openapi.License(name="CornerDevTeam"),
         ), 
    public=True, 
    permission_classes=(AllowAny,), 
    patterns=schema_url_patterns, 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/', include('bookky.urls')),
    path('swagger/?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
]

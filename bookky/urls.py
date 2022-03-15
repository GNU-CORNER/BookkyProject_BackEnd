from django.urls import path, include
from bookky import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_url_patterns = [ 
    path('v1/', include('bookky.urls')), 
    ]
schema_view = get_schema_view( 
    openapi.Info( 
        title="Django API", 
        default_version='v1', 
        terms_of_service="https://www.google.com/policies/terms/",
         ), 
        public=True, 
        permission_classes=(permissions.AllowAny,), 
        patterns=schema_url_patterns, 
        )
#url(r'^pnsApp/(?P<slug>[-a-zA-Z0-9_]+)$', views.pns_detail),
urlpatterns = [ #POST형식으로 바꿔야함
    path('test', views.read_insert),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib.auth import views as auth_views
from . import views
from .API import TeamViewSet, PersonnelViewSet, PartViewSet, AircraftViewSet, get_compatible_parts_api



# API router
router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'personnel', PersonnelViewSet)
router.register(r'parts', PartViewSet)
router.register(r'aircraft', AircraftViewSet)


# Swagger şeması
schema_view = get_schema_view(
    openapi.Info(
        title="Baykar API",
        default_version='v1',
        description="Baykar projesi için API dokümantasyonu",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Web UI URL'leri
web_ui_patterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='baykar/login.html'), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(http_method_names=['get', 'post'], template_name='baykar/logout.html'),
         name='logout'),
    path('produce-part/', views.produce_part, name='produce_part'),
    path('recycle-part/<int:part_id>/', views.recycle_part, name='recycle_part'),
    path('assemble-aircraft/', views.assemble_aircraft, name='assemble_aircraft'),
    path('api/get-compatible-parts/', views.get_compatible_parts, name='get_compatible_parts'),
]

# API URL'leri
api_patterns = [
    path('', include(router.urls)),
    path('compatible-parts/', get_compatible_parts_api, name='api-compatible-parts'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('check-session/', views.check_session, name='check_session'),

]

# Swagger URL'leri
swagger_patterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    # Web UI URL'leri doğrudan ana URL'de
    *web_ui_patterns,

    # API URL'leri
    path('api/v1/', include(api_patterns)),

    # Swagger Dökümantasyonu
    path('api/docs/', include(swagger_patterns)),
]

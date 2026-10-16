
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from dashboard import views, sustainability_views

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Main dashboard
    path("", views.home, name="home"),

    # Live camera detection
    path(
        "camera-detect/",
        views.camera_detect,
        name="camera_detect",
    ),

    # Camera detection history API
    path(
        "camera-history/",
        views.camera_history_api,
        name="camera_history_api",
    ),

    # Sustainability Hub: waste segregation, carbon impact, and action tracker
    path(
        "sustainability/",
        sustainability_views.sustainability_dashboard,
        name="sustainability",
    ),

    

path("recommendations/", views.recommendations, name="recommendations"),


path(
    "clear-calculation-history/",
    views.clear_calculation_history,
    name="clear_calculation_history",
),
path(
    "clear-camera-history/",
    views.clear_camera_history,
    name="clear_camera_history",
),



]

# Serve uploaded images during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

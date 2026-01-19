from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/gtfs/', include('gtfs.urls')),
    path('api/realtime/', include('realtime.urls')),
    path('api/evidence/', include('evidence.urls')),
]

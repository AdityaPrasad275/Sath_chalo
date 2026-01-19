from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveTripViewSet

router = DefaultRouter()
router.register(r'active-trips', ActiveTripViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

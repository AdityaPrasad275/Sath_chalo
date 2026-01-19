from rest_framework import viewsets
from .models import ActiveTrip
from .serializers import ActiveTripSerializer

class ActiveTripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActiveTrip.objects.select_related('trip', 'trip__route', 'position').all()
    serializer_class = ActiveTripSerializer

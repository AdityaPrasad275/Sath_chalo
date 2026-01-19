from rest_framework import viewsets, mixins
from .models import Observation
from .serializers import ObservationSerializer

class ObservationViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

    def perform_create(self, serializer):
        # Here we will trigger the "Evidence Layer" logic
        # For now, just save.
        serializer.save()

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Airplane
from .serializers import AirplaneSerializer
import logging


logger = logging.getLogger(__name__)


class AirplaneListCreateView(generics.ListCreateAPIView):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def create(self, request, *args, **kwargs):
        try:
            if Airplane.objects.count() >= 10:
                logger.warning("Attempted to create more than 10 airplanes.")
                return Response(
                    {"detail": "You can only assess up to 10 airplanes."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.data.get("id") is None or int(request.data.get("id")) <= 0:
                logger.warning("Invalid Airplane ID received: %s", request.data.get("id"))
                raise ValidationError({"id": "Airplane ID must be a positive integer."})
            if request.data.get("passengers") is None or int(request.data.get("passengers")) < 0:
                logger.warning("Invalid passenger count received: %s", request.data.get("passengers"))
                raise ValidationError({"passengers": "Passenger count cannot be negative."})

            logger.info("Creating airplane with ID: %s and passengers: %s",
                        request.data.get("id"), request.data.get("passengers"))
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.error("Validation error while creating airplane: %s", e.detail)
            raise
        except Exception as e:
            logger.exception("Unexpected error occurred while creating airplane: %s", str(e))
            return Response({"detail": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            if not self.queryset.exists():
                logger.info("No airplanes found in the database.")
                return Response({"message": "No airplanes found."}, status=status.HTTP_404_NOT_FOUND)

            logger.info("Fetching the list of airplanes.")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.exception("Unexpected error occurred while fetching airplane list: %s", str(e))
            return Response({"detail": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from rest_framework import viewsets, mixins, serializers, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
    Ticket
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneImageSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderSerializer
)


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @staticmethod
    def _params_to_ints(query_string: str) -> list[int]:
        """Converts a string of format '1,2,3' to a list of integers [1, 2, 3]"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        airplane_types = self.request.query_params.get("airplane_types")
        if airplane_types:
            airplane_types = AirplaneViewSet._params_to_ints(airplane_types)
            queryset = queryset.filter(airplane_type__id__in=airplane_types)

        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("airplane_type")

        return queryset.distinct()

    def get_serializer_class(self) -> type(serializers.ModelSerializer):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return self.serializer_class

    @action(
        methods=("post",),
        detail=True,
        permission_classes=IsAdminUser,
        url_path="upload-image"
    )
    def upload_image(
        self,
        request: HttpRequest,
        pk: int = None
    ) -> HttpResponse:
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

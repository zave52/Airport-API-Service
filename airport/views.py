from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from rest_framework import viewsets, mixins, serializers, status
from rest_framework.decorators import action
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
    OrderSerializer,
    OrderListRetrieveSerializer
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
    queryset = Airplane.objects.select_related("airplane_type")
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
        permission_classes=(IsAdminUser,),
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


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__closest_big_city__icontains=source)

        if destination:
            queryset = queryset.filter(destination__closest_big_city__icontains=destination)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")

        return queryset

    def get_serializer_class(self) -> type(serializers.ModelSerializer):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return self.serializer_class


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.select_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type"
        ).prefetch_related("crews")

        route = self.request.query_params.get("route")

        if route:
            source, destination = route.split("-")
            queryset = queryset.filter(
                route__source__closest_big_city__icontains=source,
                route__destination__closest_big_city__icontains=destination
            )

        return queryset

    def get_serializer_class(self) -> type(serializers.ModelSerializer):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return self.serializer_class


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__flight")

        return queryset

    def get_serializer_class(self) -> type(serializers.ModelSerializer):
        if self.action in ("list", "retrieve"):
            return OrderListRetrieveSerializer
        return self.serializer_class

    def perform_create(
        self,
        serializer: type(serializers.ModelSerializer)
    ) -> None:
        serializer.save(user=self.request.user)

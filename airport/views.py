from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
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

    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all airplane types."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new airplane type."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing airplane type."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific airplane type."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update an airplane type."""
        return super().partial_update(request, *args, **kwargs)


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
        """
        Converts a string of format '1,2,3' to a list of integers [1, 2, 3]
        """
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

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "Image file to upload"
                    }
                },
                "required": ["image"]
            }
        }
    )
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
        """
        Upload an image for a specific airplane.
        Only accessible by admin users.
        """
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_types",
                type={"type": "list", "items": {"type": "integer"}},
                description="Filter airplanes by their type IDs "
                            "(ex. ?airplane_types=1,2)."
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all airplanes."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new airplane."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing airplane."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific airplane."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update an airplane."""
        return super().partial_update(request, *args, **kwargs)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all airports."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new airport."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing airport."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific airport."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update an airport."""
        return super().partial_update(request, *args, **kwargs)


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
            queryset = queryset.filter(
                source__closest_big_city__icontains=source
            )

        if destination:
            queryset = queryset.filter(
                destination__closest_big_city__icontains=destination
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")

        return queryset

    def get_serializer_class(self) -> type(serializers.ModelSerializer):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[

            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter routes by source airport's "
                            "closest big city (ex. ?source=Kyiv)."
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter routes by destination airport's closest "
                            "big city (ex. ?destination=Lviv)."
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all routes."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new route."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing route."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific route."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update a route."""
        return super().partial_update(request, *args, **kwargs)


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all crews."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new crew."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing crew."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific crew."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update a crew."""
        return super().partial_update(request, *args, **kwargs)


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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter flights by route (ex. ?route=Kyiv-Lviv)."
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of all flights."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new flight."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing flight."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Retrieve details of a specific flight."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update a flight."""
        return super().partial_update(request, *args, **kwargs)


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

    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get a list of orders for the currently authenticated user."""
        return super().list(request, *args, **kwargs)

    def create(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a new order for the currently authenticated user."""
        return super().create(request, *args, **kwargs)

    def update(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Update an existing order for the currently authenticated user."""
        return super().update(request, *args, **kwargs)

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Retrieve details of a specific order for
        the currently authenticated user.
        """
        return super().retrieve(request, *args, **kwargs)

    def partial_update(
        self,
        request: HttpRequest,
        *args,
        **kwargs
    ) -> HttpResponse:
        """Partially update an order for the currently authenticated user."""
        return super().partial_update(request, *args, **kwargs)

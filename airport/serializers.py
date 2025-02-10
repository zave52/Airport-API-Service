from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

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


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "rows", "seats_in_row", "capacity", "airplane_type",
            "image"
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "capacity", "airplane_type", "image")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        Route.validate_source_and_destination(
            attrs["source"],
            attrs["destination"],
            ValidationError
        )
        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="closest_big_city"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="closest_big_city"
    )


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crews"
        )

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        Flight.validate_departure_and_arrival_time(
            attrs["departure_time"],
            attrs["arrival_time"],
            ValidationError
        )
        return data


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "departure_time")


class FlightSmallListSerializer(FlightSerializer):
    route = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = ("id", "route", "departure_time")

    @staticmethod
    def get_route(obj: Flight) -> str:
        return f"{obj.route.source.closest_big_city}-{obj.route.destination.closest_big_city}"


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crews = SlugRelatedField(many=True, read_only=True, slug_field="full_name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs: dict) -> dict:
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    flight = FlightSmallListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_time", "tickets")

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListRetrieveSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

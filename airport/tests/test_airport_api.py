from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirportSerializer, AirplaneListSerializer
)

AIRPLANE_TYPES_URL = reverse("airport:airplanetype-list")
AIRPLANES_URL = reverse("airport:airplane-list")
AIRPORTS_URL = reverse("airport:airport-list")
ROUTES_URL = reverse("airport:route-list")
CREWS_URL = reverse("airport:crew-list")
FLIGHTS_URL = reverse("airport:flight-list")
ORDERS_URL = reverse("airport:order-list")


def sample_airport(**params: dict) -> Airport:
    defaults = {
        "name": "Test Airport",
        "closest_big_city": "Test City"
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_airplane_type(**params: dict) -> AirplaneType:
    defaults = {"name": "Test Type"}
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params: dict) -> Airplane:
    airplane_type = params.pop("airplane_type", sample_airplane_type())
    defaults = {
        "name": "Test Airplane",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class PublicAirportApiTests(TestCase):
    """Test unauthenticated airport API access."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test that authentication is required."""
        urls = [
            AIRPLANE_TYPES_URL,
            AIRPLANES_URL,
            AIRPORTS_URL,
            ROUTES_URL,
            CREWS_URL,
            FLIGHTS_URL,
            ORDERS_URL
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAirportApiTests(TestCase):
    """Test authenticated airport API access."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass123"
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane_types(self) -> None:
        """Test retrieving airplane types."""
        sample_airplane_type()
        sample_airplane_type(name="Another type")

        res = self.client.get(AIRPLANE_TYPES_URL)

        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_list_airports(self) -> None:
        """Test retrieving airports."""
        sample_airport()
        sample_airport(name="Another Airport", closest_big_city="Another City")

        res = self.client.get(AIRPORTS_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_list_orders(self) -> None:
        """Test retrieving orders."""
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.user)

        res = self.client.get(reverse("airport:order-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_filter_routes_by_airports(self) -> None:
        """Test filtering routes by source and destination airports."""
        source1 = sample_airport(closest_big_city="Source 1")
        source2 = sample_airport(closest_big_city="Source 1")
        dest1 = sample_airport(closest_big_city="Destination 1")
        dest2 = sample_airport(closest_big_city="Destination 2")

        route1 = Route.objects.create(
            source=source1,
            destination=dest1,
            distance=1000
        )
        route2 = Route.objects.create(
            source=source2,
            destination=dest2,
            distance=2000
        )

        res = self.client.get(
            ROUTES_URL,
            {
                "source": source1.closest_big_city,
                "destination": dest1.closest_big_city
            }
        )

        response_data = res.data["results"]

        self.assertTrue(any(item["id"] == route1.id for item in response_data))
        self.assertFalse(any(item["id"] == route2.id for item in response_data))

    def test_filter_airplanes_by_airplane_type(self) -> None:
        airplane_type_1 = sample_airplane_type(name="Type 1")
        airplane_type_2 = sample_airplane_type(name="Type 2")

        airplane_without_type = sample_airplane()
        airplane_with_type_1 = sample_airplane(
            name="Airplane 1",
            airplane_type=airplane_type_1
        )
        airplane_with_type_2 = sample_airplane(
            name="Airplane 2",
            airplane_type=airplane_type_2
        )

        res = self.client.get(
            AIRPLANES_URL,
            {"airplane_types": f"{airplane_type_1.id},{airplane_type_2.id}"}
        )

        serializer_without_type = AirplaneListSerializer(airplane_without_type)
        serializer_type_1 = AirplaneListSerializer(airplane_with_type_1)
        serializer_type_2 = AirplaneListSerializer(airplane_with_type_2)

        self.assertIn(serializer_type_1.data, res.data["results"])
        self.assertIn(serializer_type_2.data, res.data["results"])
        self.assertNotIn(
            serializer_without_type.data,
            res.data["results"]
        )

    def test_filter_flights_by_route(self) -> None:
        """Test filtering flights by route"""
        route1 = Route.objects.create(
            source=sample_airport(closest_big_city="Source 1"),
            destination=sample_airport(closest_big_city="Dest 1"),
            distance=1000
        )
        route2 = Route.objects.create(
            source=sample_airport(closest_big_city="Source 2"),
            destination=sample_airport(closest_big_city="Dest 2"),
            distance=2000
        )
        airplane = sample_airplane()

        flight1 = Flight.objects.create(
            route=route1,
            airplane=airplane,
            departure_time="2024-03-01T10:00:00Z",
            arrival_time="2024-03-01T12:00:00Z"
        )
        flight2 = Flight.objects.create(
            route=route2,
            airplane=airplane,
            departure_time="2024-03-01T10:00:00Z",
            arrival_time="2024-03-01T12:00:00Z"
        )

        res = self.client.get(
            FLIGHTS_URL,
            {
                "route": f"{route1.source.closest_big_city}-"
                         f"{route1.destination.closest_big_city}"
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], flight1.id)


class AdminAirportApiTests(TestCase):
    """Test airport API for admin users."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self) -> None:
        """Test creating airplane type."""
        payload = {"name": "New Type"}
        res = self.client.post(AIRPLANE_TYPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])
        self.assertEqual(airplane_type.name, payload["name"])



    def test_create_route(self) -> None:
        """Test creating a route."""
        source = sample_airport()
        destination = sample_airport(name="Destination Airport")

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 1000
        }
        res = self.client.post(ROUTES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(route.source, source)
        self.assertEqual(route.destination, destination)

    def test_create_flight(self) -> None:
        """Test creating a flight."""
        route = Route.objects.create(
            source=sample_airport(),
            destination=sample_airport(closest_big_city="Destination"),
            distance=1000
        )
        airplane = sample_airplane()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2024-03-01T10:00:00Z",
            "arrival_time": "2024-03-01T12:00:00Z"
        }
        res = self.client.post(FLIGHTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route, route)
        self.assertEqual(flight.airplane, airplane)

    def test_create_order(self) -> None:
        """Test creating a new order."""
        route = Route.objects.create(
            source=sample_airport(closest_big_city="Source"),
            destination=sample_airport(closest_big_city="Destination"),
            distance=1000
        )

        airplane = sample_airplane()
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2024-03-01T10:00:00Z",
            arrival_time="2024-03-01T12:00:00Z"
        )

        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 1,
                    "seat": 1
                }
            ]
        }

        res = self.client.post(
            reverse("airport:order-list"),
            payload,
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 1)

    def test_create_order_invalid_seat(self) -> None:
        """Test creating order with invalid seat."""
        route = Route.objects.create(
            source=sample_airport(closest_big_city="Source"),
            destination=sample_airport(closest_big_city="Destination"),
            distance=1000
        )
        airplane = sample_airplane(rows=5, seats_in_row=6)
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2024-03-01T10:00:00Z",
            arrival_time="2024-03-01T12:00:00Z"
        )

        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 10,
                    "seat": 1
                }
            ]
        }

        res = self.client.post(
            reverse("airport:order-list"),
            payload,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

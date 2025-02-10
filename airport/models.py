import pathlib
import uuid
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.text import slugify


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.name)}-{uuid.uuid4()}" + pathlib.Path(
        filename
    ).suffix
    )
    return pathlib.Path("upload/airplanes/") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(validators=(MinValueValidator(1),))
    seats_in_row = models.IntegerField(validators=(MinValueValidator(1),))
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.closest_big_city


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes"
    )
    distance = models.IntegerField(validators=(MinValueValidator(1),))

    @staticmethod
    def validate_source_and_destination(
        source: Airport,
        destination: Airport,
        error_to_raise: type(Exception)
    ) -> None:
        if source is None or destination is None:
            raise error_to_raise("Both source and destination must exist.")
        if source.id == destination.id:
            raise error_to_raise("Source and destination cannot be the same.")

    def clean(self) -> None:
        Route.validate_source_and_destination(
            self.source,
            self.destination,
            ValidationError
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str = None,
        update_fields: list[str] = None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.source}-{self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="flights", blank=True)

    @staticmethod
    def validate_departure_and_arrival_time(
        departure: datetime,
        arrival: datetime,
        error_to_raise: type(Exception)
    ) -> None:
        if departure >= arrival:
            raise error_to_raise("Departure time must be before arrival time.")

    def clean(self) -> None:
        Flight.validate_departure_and_arrival_time(
            self.departure_time,
            self.arrival_time,
            ValidationError
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str = None,
        update_fields: list[str] = None,
    ) -> None:
        self.full_clean()
        return super(Flight, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{self.route} ({self.departure_time})"


class Order(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ("-created_time",)

    def __str__(self) -> str:
        return str(self.created_time)


class Ticket(models.Model):
    row = models.IntegerField(validators=(MinValueValidator(1),))
    seat = models.IntegerField(validators=(MinValueValidator(1),))
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="unique_ticket_seat_trip"
            )
        ]

    @staticmethod
    def validate_ticket(
        row: int,
        seat: int,
        airplane: Airplane,
        error_to_raise: type(Exception)
    ) -> None:
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in (
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ):
            count_attrs = getattr(airplane, airplane_attr_name),
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number "
                                          f"must be in available range:"
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str = None,
        update_fields: list[str] = None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{self.flight} (row - {self.row}, seat - {self.seat})"

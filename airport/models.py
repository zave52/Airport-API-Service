from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(validators=(MinValueValidator(1),))
    seats_in_row = models.IntegerField(validators=(MinValueValidator(1),))
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(source=models.F("destination")),
                name="prevent_same_source_and_destination"
            )
        ]

    def __str__(self) -> str:
        return f"{self.source}-{self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(departure_time__lt=models.F("arrival_time")),
                name="check_departure_before_arrival"
            )
        ]

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

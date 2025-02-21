import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


def play_image_path(instance: "Play", filename: str) -> pathlib.Path:
    filename = (f"{slugify(instance.title)}-"
                f"{uuid.uuid4()}") + pathlib.Path(filename).suffix
    return pathlib.Path("upload/plays") / pathlib.Path(filename)


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name="plays", blank=True)
    actors = models.ManyToManyField(Actor, related_name="plays", blank=True)
    image = models.ImageField(null=True, upload_to=play_image_path)

    def __str__(self):
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return (f"Hall: {self.name}, rows: {self.rows}, "
                f"seats in row: {self.seats_in_row}")


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall, on_delete=models.CASCADE, related_name="performances"
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return (f"Play: {self.play.title}, "
                f"theatre hall: {self.theatre_hall.name}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        "Reservation",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ("row", "seat", "performance")

    def __str__(self):
        return (f"Play: {self.performance.play.title}, "
                f"Hall: {self.performance.theatre_hall.name}, "
                f"Row: {self.row}, seat: {self.seat}.")

    @staticmethod
    def ticket_validate(
            row: int, seat: int, rows_in_hall, seats_in_row: int, error
    ):
        if not (1 <= row <= rows_in_hall):
            raise error(
                {
                    "row": f"Row must be in range "
                           f"[1, {rows_in_hall}], not {row}."
                }
            )
        if not (1 <= seat <= seats_in_row):
            raise error(
                {
                    "seat": f"Seat must be in range "
                            f"[1, {seats_in_row}], not {seat}"
                }
            )

    def clean(self):
        self.ticket_validate(
            self.row,
            self.seat,
            self.performance.theatre_hall.rows,
            self.performance.theatre_hall.seats_in_row,
            ValueError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    def __str__(self):
        return f"{self.created_at}"

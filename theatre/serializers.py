from django.db import transaction
from rest_framework import serializers

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation
)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ("id", "name")


class ActorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class PlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Play
        fields = ("id", "title", "description", "genres", "actors")


class PlayListSerializer(PlaySerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    actors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )


class PlayRetrieveSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)


class ItemImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Play
        fields = ("id", "image")


class TheatreHallSerializer(serializers.ModelSerializer):

    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="title"
    )
    theatre_hall = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "play",
            "theatre_hall",
            "show_time",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.ticket_validate(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall.rows,
            attrs["performance"].theatre_hall.seats_in_row,
            serializers.ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(read_only=True)


class TakenSeatsInRowSerializer(TicketSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat")


class PerformanceRetrieveSerializer(PerformanceSerializer):
    play = PlayRetrieveSerializer(many=False, read_only=True)
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    taken_seats = TakenSeatsInRowSerializer(
        many=True,
        read_only=True,
        source="tickets"
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time", "taken_seats")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

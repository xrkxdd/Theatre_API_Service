from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from theatre.models import (
    Reservation,
    Ticket,
    Play,
    TheatreHall,
    Performance
)


RESERVATION_URL = reverse("theater:reservation-list")

class UnauthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)
        self.play = Play.objects.create(
            title="Test Title",
            description="Test Description"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Great Arena",
            rows=20,
            seats_in_row=20
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time="2024-10-15 18:00"
        )

    def test_reservation_list(self):
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            row=1,
            seat=1,
            performance=self.performance,
            reservation=reservation
        )
        Ticket.objects.create(
            row=1,
            seat=2,
            performance=self.performance,
            reservation=reservation
        )

        res = self.client.get(RESERVATION_URL)
        print(res.data["results"][0]["tickets"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["results"], list)
        self.assertEqual(len(res.data["results"][0]["tickets"]), 2)

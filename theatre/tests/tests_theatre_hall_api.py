from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer


def sample_theatre_hall(**params) -> TheatreHall:
    defaults = {
        "name": "Test Hall",
        "rows": 20,
        "seats_in_row": 20
    }
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)

def detail_url(theatre_hall_id):
    return reverse("theater:theatre-hall-detail", args=(theatre_hall_id,))

THEATRE_HALL_URL = reverse("theater:theatre-hall-list")

class UnauthenticatedTheatreHallTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTheatreHallTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_theatre_halls_list(self):
        sample_theatre_hall()
        sample_theatre_hall(name="Great Arena")

        res = self.client.get(THEATRE_HALL_URL)
        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_halls, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_theatre_hall_detail(self):
        theatre_hall = sample_theatre_hall()

        url = detail_url(theatre_hall.id)
        res = self.client.get(url)

        serializer = TheatreHallSerializer(theatre_hall)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_theatre_hall_forbidden(self):
        payload = {
            "name": "Test Hall",
            "rows": 20,
            "seats_in_row": 20
        }

        res = self.client.post(THEATRE_HALL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTheatreHallTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        payload = {
            "name": "Test Hall",
            "rows": 20,
            "seats_in_row": 20
        }

        res = self.client.post(THEATRE_HALL_URL, payload)
        theatre_hall = TheatreHall.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(theatre_hall, key))

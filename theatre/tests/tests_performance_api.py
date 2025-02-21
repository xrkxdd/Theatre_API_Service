from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from theatre.models import Performance, Play, TheatreHall


PERFORMANCE_URL = reverse("theater:performance-list")

class UnauthenticatedPerformanceApi(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_performance_list(self):
        play = Play.objects.create(
            title="Test Title",
            description="Test Description"
        )
        theatre_hall = TheatreHall.objects.create(
            name="Great Arena",
            rows=20,
            seats_in_row=20
        )
        Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-10-15 18:00",
        )
        Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-10-16 18:00",
        )

        res = self.client.get(PERFORMANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["results"], list)
        self.assertEqual(len(res.data["results"]), 2)

    def test_retrieve_performance_detail(self):
        play = Play.objects.create(
            title="Test Title",
            description="Test Description"
        )
        theatre_hall = TheatreHall.objects.create(
            name="Great Arena",
            rows=20,
            seats_in_row=20
        )
        performance = Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-10-15 18:00",
        )
        url = reverse("theater:performance-detail", args=(performance.id,))

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["play"]["title"], performance.play.title)
        self.assertEqual(res.data["theatre_hall"]["name"], performance.theatre_hall.name)

    def test_create_performance_forbidden(self):
        play = Play.objects.create(
            title="Test Title",
            description="Test Description"
        )
        theatre_hall = TheatreHall.objects.create(
            name="Great Arena",
            rows=20,
            seats_in_row=20
        )
        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-10-15"
        }

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPerformanceApiTests(TestCase):
    def setUp(self):
        self.client =APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_performance(self):
        play = Play.objects.create(
            title="Test Title",
            description="Test Description"
        )
        theatre_hall = TheatreHall.objects.create(
            name="Great Arena",
            rows=20,
            seats_in_row=20
        )
        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-10-15 18:00"
        }

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

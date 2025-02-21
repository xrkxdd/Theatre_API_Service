from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Genre
from theatre.serializers import GenreSerializer


def sample_genre(**params) -> Genre:
    defaults = {
        "name": "Drama"
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)

def detail_url(genre_id):
    return reverse("theater:genre-detail", args=(genre_id,))

GENRE_URL = reverse("theater:genre-list")

class UnauthenticatedGenreApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedGenreApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_genres_list(self):
        sample_genre()
        sample_genre(name="Action")

        res = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_genre_detail(self):
        genre = sample_genre()

        url = detail_url(genre.id)

        res = self.client.get(url)
        serializer = GenreSerializer(genre)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre_forbidden(self):
        payload = {
            "name": "Action"
        }
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_genre(self):
        payload = {
            "name": "Drama"
        }

        res = self.client.post(GENRE_URL, payload)
        genre = Genre.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(genre, key))

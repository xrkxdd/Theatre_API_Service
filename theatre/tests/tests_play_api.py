from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status

from theatre.models import Play, Actor, Genre
from theatre.serializers import PlayListSerializer, PlayRetrieveSerializer

PLAY_URL = reverse("theater:play-list")

def sample_play(**params) -> Play:
    defaults = {
        "title": "TestTitle",
        "description": "Test Description"
    }
    defaults.update(params)
    return Play.objects.create(**defaults)

def detail_url(play_id):
    return reverse("theater:play-detail", args=(play_id,))


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_plays_list(self):
        sample_play()
        play_with_actors_and_genres = sample_play(
            title="Play with genres and actors"
        )

        actor = Actor.objects.create(first_name="Harry", last_name="Potter")
        genre = Genre.objects.create(name="Fantasy")

        play_with_actors_and_genres.actors.add(actor)
        play_with_actors_and_genres.genres.add(genre)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer  = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_plays_by_actors_and_genres(self):
        play_without_actors_and_genres = sample_play()
        play_with_actors_and_genres_1 = sample_play(
            title="Dune"
        )
        play_with_actors_and_genres_2 = sample_play(
            title="Titanic"
        )

        actor_1 = Actor.objects.create(
            first_name="Leonardo",
            last_name="DiCaprio"
        )
        actor_2 = Actor.objects.create(
            first_name="Kate",
            last_name="Winslet"
        )
        actor_3 = Actor.objects.create(
            first_name="Timothy",
            last_name="Shalame"
        )
        actor_4 = Actor.objects.create(
            first_name="Zendaya",
            last_name="Coleman"
        )
        genre_1 = Genre.objects.create(name="Drama")
        genre_2 = Genre.objects.create(name= "Fantastic")

        play_with_actors_and_genres_1.actors.add(actor_3, actor_4)
        play_with_actors_and_genres_1.genres.add(genre_2)
        play_with_actors_and_genres_2.actors.add(actor_1, actor_2)
        play_with_actors_and_genres_2.genres.add(genre_1)

        res = self.client.get(
            PLAY_URL,
            {
                "actors": f"{actor_1.id},{actor_2.id}",
                "genres": f"{genre_1.id}"
            }
        )

        serializer_without_actors_and_genres = PlayListSerializer(play_without_actors_and_genres)
        serializer_with_actors_and_genres_1 = PlayListSerializer(play_with_actors_and_genres_1)
        serializer_with_actors_and_genres_2 = PlayListSerializer(play_with_actors_and_genres_2)

        self.assertNotIn(serializer_with_actors_and_genres_1.data, res.data["results"])
        self.assertIn(serializer_with_actors_and_genres_2.data, res.data["results"])
        self.assertNotIn(serializer_without_actors_and_genres.data, res.data["results"])

    def test_retrieve_play_detail(self):
        play = sample_play()
        actor = Actor.objects.create(
            first_name="Leonardo",
            last_name="DiCaprio"
        )
        genre = Genre.objects.create(name="Drama")
        play.actors.add(actor)
        play.genres.add(genre)

        url = detail_url(play.id)

        res = self.client.get(url)

        serializer = PlayRetrieveSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "Test Title",
            "description": "Test Description"
        }

        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        payload = {
            "title": "Test Title",
            "description": "Test Description"
        }

        res = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(play, key))

    def test_create_play_with_authors_and_genres(self):
        actor = Actor.objects.create(
            first_name="Orlando",
            last_name="Blum"
        )
        genre = Genre.objects.create(name="Action")

        payload = {
            "title": "Test Title",
            "description": "Test Description",
            "actors": [actor.id],
            "genres": [genre.id]
        }

        res = self.client.post(PLAY_URL, payload)

        play = Play.objects.get(id=res.data["id"])
        actors = play.actors.all()
        genres = play.genres.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(actor, actors)
        self.assertIn(genre, genres)

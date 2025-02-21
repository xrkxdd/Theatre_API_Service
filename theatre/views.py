from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Reservation,
)
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayRetrieveSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceRetrieveSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ItemImageSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()

    @staticmethod
    def _params_to_ints(query_string):
        """
        Converts a string of format '1,2,3' to a list of integers [1, 2, 3].
        """
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayRetrieveSerializer
        elif self.action == "upload_image":
            return ItemImageSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset

        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        if genres:
            genres = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres)

        if actors:
            actors = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("genres", "actors")

        return queryset.distinct()

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by actors id (ex. ?actors=2,3)"
            ),
            OpenApiParameter(
                "genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by genres id (ex. ?genres=1,3)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of plays."""
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceRetrieveSerializer

        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        play = self.request.query_params.get("play")

        if play:
            queryset = queryset.filter(play__title__icontains=play)

        if self.action == "list":
            queryset = (
                queryset.select_related("play", "theatre_hall")
                .annotate(
                    tickets_available=F("theatre_hall__rows")
                    * F("theatre_hall__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")

        if self.action == "retrieve":
            queryset = queryset.select_related("play", "theatre_hall")

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "play",
                type={"type": "string"},
                description="Filter by play title (ex. ?play=titanic)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances"""
        return super().list(request, *args, **kwargs)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall"
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("tickets__performance")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return ReservationSerializer

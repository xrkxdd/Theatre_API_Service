from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet,
    TheatreHallViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)


router = routers.DefaultRouter()
router.register("genres", GenreViewSet, basename="genre")
router.register("actors", ActorViewSet, basename="actor")
router.register("plays", PlayViewSet, basename="play")
router.register(
    "theatre-halls",
    TheatreHallViewSet,
    basename="theatre-hall"
)
router.register(
    "performances",
    PerformanceViewSet,
    basename="performance"
)
router.register(
    "reservations",
    ReservationViewSet,
    basename="reservation"
)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "theater"

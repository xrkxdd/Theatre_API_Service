from django.contrib import admin
from django.contrib.admin import TabularInline, ModelAdmin

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation
)


class TicketInline(TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Play)
admin.site.register(TheatreHall)
admin.site.register(Performance)

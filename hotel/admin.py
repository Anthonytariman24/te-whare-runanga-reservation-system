
from django.contrib import admin
from .models import Room, Reservation, Notification
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number','room_type','price','is_active')
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id','customer','room','check_in','check_out','status','created_at')
    list_filter = ('status',)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','message','read','created_at')

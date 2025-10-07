
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

STATUS_CHOICES = (
    ('PENDING','Pending'),
    ('APPROVED','Approved'),
    ('CANCELLED','Cancelled'),
)
class Room(models.Model):
    number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number} ({self.room_type})"

    def is_occupied(self):
        """I-check kung ang room ay may active reservation."""
        today = date.today()
        return self.reservations.filter(
            status__in=['APPROVED', 'PENDING'],
            check_out__gte=today
        ).exists()

class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Reservation {self.id} - {self.room} for {self.customer.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Notification to {self.user.username}: {self.message}"

from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('CANCELLED', 'Cancelled'),
)

class Room(models.Model):
    number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.number} - {self.name or 'Room'}"

class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation #{self.id} - {self.customer.username} - {self.room}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif to {self.user.username}: {self.message[:40]}"

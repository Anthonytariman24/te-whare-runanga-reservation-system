
# Run with: python create_sample_data.py (after installing Django and running migrations)
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','hotel_project.settings')
import django
django.setup()
from hotel.models import Room
if Room.objects.count() == 0:
    Room.objects.create(number='101', room_type='Single', price=1000, description='Single room')
    Room.objects.create(number='102', room_type='Double', price=1800, description='Double room')
    Room.objects.create(number='201', room_type='Suite', price=3500, description='Suite room')
    print('Sample rooms created')
else:
    print('Rooms already exist')

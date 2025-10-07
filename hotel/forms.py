from django import forms
from .models import Room, Reservation
from django.contrib.auth.forms import AuthenticationForm

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'name', 'description', 'price', 'is_available']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

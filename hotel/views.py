from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Room, Reservation, Notification
from .forms import RoomForm, ReservationForm
from django.contrib.auth.models import User
from django.utils import timezone

def home(request):
    return redirect('rooms')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('rooms')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('rooms')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'hotel/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('login')

def available_rooms(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'hotel/rooms.html', {'rooms': rooms})

@login_required
def make_reservation(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.room = room
            reservation.status = 'PENDING'
            reservation.save()
            Notification.objects.create(user=request.user, message=f"Reservation {reservation.id} created (Pending).")
            messages.success(request, 'Reservation created and is pending approval.')
            return redirect('my_reservations')
    else:
        form = ReservationForm(initial={'room': room})
    return render(request, 'hotel/make_reservation.html', {'form': form, 'room': room})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'hotel/my_reservations.html', {'reservations': reservations})

@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'hotel/notifications.html', {'notifications': notes})

def staff_check(user):
    return user.is_staff

@login_required
@user_passes_test(staff_check)
def admin_dashboard(request):
    rooms = Room.objects.all()
    return render(request, 'hotel/admin_dashboard.html', {'rooms': rooms})

@login_required
@user_passes_test(staff_check)
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created.')
            return redirect('admin_dashboard')
    else:
        form = RoomForm()
    return render(request, 'hotel/room_form.html', {'form': form, 'title': 'Create Room'})

@login_required
@user_passes_test(staff_check)
def update_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated.')
            return redirect('admin_dashboard')
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotel/room_form.html', {'form': form, 'title': 'Update Room'})

@login_required
@user_passes_test(staff_check)
def list_reservations(request):
    reservations = Reservation.objects.order_by('-created_at')
    return render(request, 'hotel/list_reservations.html', {'reservations': reservations})

@login_required
@user_passes_test(staff_check)
def approve_reservation(request, pk):
    r = get_object_or_404(Reservation, pk=pk)
    r.status = 'APPROVED'
    r.save()
    Notification.objects.create(user=r.customer, message=f"Your reservation #{r.id} has been approved.")
    messages.success(request, 'Reservation approved.')
    return redirect('list_reservations')

@login_required
@user_passes_test(staff_check)
def cancel_reservation(request, pk):
    r = get_object_or_404(Reservation, pk=pk)
    r.status = 'CANCELLED'
    r.save()
    Notification.objects.create(user=r.customer, message=f"Your reservation #{r.id} has been cancelled.")
    messages.success(request, 'Reservation cancelled.')
    return redirect('list_reservations')

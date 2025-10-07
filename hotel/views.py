from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Reservation, Notification
from .forms import ReservationForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout







@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('hotel:home')





def home(request):
    return render(request, 'hotel/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.is_staff = False  # ensure it's a customer
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}, your account has been created!')
            return redirect('hotel:room_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# -------------------
# User type helpers
# -------------------

def is_admin(user):
    return user.is_staff

def is_customer(user):
    return not user.is_staff


# -------------------
# Customer-only views
# -------------------

@login_required
@user_passes_test(is_customer)
def room_list(request):
    rooms = Room.objects.filter(is_active=True)
    return render(request, 'hotel/room_list.html', {'rooms': rooms})


@login_required
@user_passes_test(is_customer)
def make_reservation(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_active=True)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.room = room
            res.customer = request.user
            res.save()
            Notification.objects.create(user=request.user,
                                        message=f"Reservation {res.id} created and pending approval")
            messages.success(request, 'Reservation created and pending approval.')
            return redirect('hotel:my_reservations')
    else:
        form = ReservationForm(initial={'room': room.id})
    return render(request, 'hotel/make_reservation.html', {'form': form, 'room': room})


@login_required
@user_passes_test(is_customer)
def my_reservations(request):
    reservations = request.user.reservations.all().order_by('-created_at')
    return render(request, 'hotel/my_reservations.html', {'reservations': reservations})


@login_required
@user_passes_test(is_customer)
def notifications(request):
    notes = request.user.notifications.all().order_by('-created_at')
    return render(request, 'hotel/notifications.html', {'notifications': notes})


# -------------------
# Admin-only views
# -------------------

@login_required
@user_passes_test(is_admin)
def admin_reservations(request):
    reservations = Reservation.objects.all().order_by('-created_at')
    return render(request, 'hotel/admin_reservations.html', {'reservations': reservations})


@login_required
@user_passes_test(is_admin)
def approve_reservation(request, res_id):
    res = get_object_or_404(Reservation, id=res_id)
    res.status = 'APPROVED'
    res.save()
    Notification.objects.create(user=res.customer, message=f"Your reservation {res.id} was APPROVED")
    return redirect('hotel:admin_reservations')


@login_required
@user_passes_test(is_admin)
def cancel_reservation(request, res_id):
    res = get_object_or_404(Reservation, id=res_id)
    res.status = 'CANCELLED'
    res.save()
    Notification.objects.create(user=res.customer, message=f"Your reservation {res.id} was CANCELLED")
    return redirect('hotel:admin_reservations')



@login_required
@user_passes_test(is_admin)
def manage_rooms(request):
    rooms = Room.objects.all().order_by('number')
    return render(request, 'hotel/manage_rooms.html', {'rooms': rooms})

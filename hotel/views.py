from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Room, Reservation, Notification
from .forms import ReservationForm, UserRegistrationForm, LoginForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from datetime import date

# -------------------
# Authentication Views
# -------------------

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
    return render(request, 'register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {user.username}!')
            if user.is_staff:
                return redirect('hotel:admin_reservations')
            else:
                return redirect('hotel:room_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('hotel:home')


# -------------------
# User Type Helpers
# -------------------

def is_admin(user):
    return user.is_staff

def is_customer(user):
    return not user.is_staff


# -------------------
# Customer Views
# -------------------
# @login_required
# @user_passes_test(is_customer)
def room_list(request):
    today = date.today()
    rooms = Room.objects.filter(is_active=True).exclude(
        reservations__status='APPROVED',
        reservations__check_out__gte=today
    ).distinct()
    occupied_rooms = Room.objects.filter(
        is_active=True,
        reservations__status='APPROVED',
        reservations__check_out__gte=today
    ).distinct()
    for room in occupied_rooms:
        latest_reservation = room.reservations.filter(
            status='APPROVED',
            check_out__gte=today
        ).order_by('-check_in').first()
        room.check_in = latest_reservation.check_in if latest_reservation else None
        room.check_out = latest_reservation.check_out if latest_reservation else None
    user_reservations = {}
    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(customer=request.user).order_by('-created_at')
        for res in reservations:
            if res.room.id not in user_reservations:
                user_reservations[res.room.id] = res.status
    context = {
        'rooms': rooms,
        'occupied_rooms': occupied_rooms,
        'user_reservations': user_reservations,
    }
    return render(request, 'hotel/room_list.html', context)


@login_required
@user_passes_test(is_customer)
def make_reservation(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_active=True)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            if check_in >= check_out:
                messages.error(request, "Check-out date must be after check-in.")
                return render(request, 'hotel/make_reservation.html', {'form': form, 'room': room})
            res = form.save(commit=False)
            res.room = room
            res.customer = request.user
            res.save()
            Notification.objects.create(
                user=request.user,
                message=f"Reservation {res.id} created and pending approval"
            )
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
# Admin Views
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
    Notification.objects.create(
        user=res.customer,
        message=f"Your reservation {res.id} was APPROVED"
    )
    messages.success(request, f"Reservation {res.id} approved.")
    return redirect('hotel:admin_reservations')


@login_required
@user_passes_test(is_admin)
def cancel_reservation(request, res_id):
    res = get_object_or_404(Reservation, id=res_id)
    res.status = 'CANCELLED'
    res.save()
    Notification.objects.create(
        user=res.customer,
        message=f"Your reservation {res.id} was CANCELLED"
    )
    messages.success(request, f"Reservation {res.id} cancelled.")
    return redirect('hotel:admin_reservations')


@login_required
@user_passes_test(is_admin)
def manage_rooms(request):
    rooms = Room.objects.all().order_by('number')
    return render(request, 'hotel/manage_rooms.html', {'rooms': rooms})


@login_required
@user_passes_test(is_admin)
def add_room(request):
    if request.method == "POST":
        number = request.POST.get("number")
        room_type = request.POST.get("room_type")
        price = request.POST.get("price")
        description = request.POST.get("description")
        if not number or not price:
            return JsonResponse({"success": False, "error": "Number and Price are required."})
        room = Room.objects.create(
            number=number,
            room_type=room_type,
            price=price,
            description=description,
            is_active=True
        )
        return JsonResponse({
            "success": True,
            "room": {
                "number": room.number,
                "room_type": room.room_type,
                "price": str(room.price),
                "description": room.description
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
@user_passes_test(is_admin)
def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        number = request.POST.get("number")
        room_type = request.POST.get("room_type")
        price = request.POST.get("price")
        description = request.POST.get("description")
        if not number or not price:
            return JsonResponse({"success": False, "error": "Number and Price are required."})
        room.number = number
        room.room_type = room_type
        room.price = price
        room.description = description
        room.save()
        return JsonResponse({
            "success": True,
            "room": {
                "number": room.number,
                "room_type": room.room_type,
                "price": str(room.price),
                "description": room.description
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
@user_passes_test(is_admin)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        room.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method."})


# -------------------
# User Management Views
# -------------------

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().order_by('username')
    return render(request, 'hotel/manage_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_staff = request.POST.get("is_staff") == "on"

        if not username or not password:
            return JsonResponse({"success": False, "error": "Username and password are required."})

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": "Username already exists."})

        user = User.objects.create(
            username=username,
            email=email,
            is_staff=is_staff,
            password=make_password(password)
        )
        return JsonResponse({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        is_staff = request.POST.get("is_staff") == "on"
        password = request.POST.get("password")

        if not username:
            return JsonResponse({"success": False, "error": "Username is required."})

        user.username = username
        user.email = email
        user.is_staff = is_staff
        if password:
            user.password = make_password(password)
        user.save()

        return JsonResponse({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        if user.is_superuser:
            return JsonResponse({"success": False, "error": "Cannot delete a superuser!"})
        user.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method."})

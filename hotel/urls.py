from django.urls import path
from . import views

urlpatterns = [
    # public / customer
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('rooms/', views.available_rooms, name='rooms'),
    path('reserve/<int:room_id>/', views.make_reservation, name='make_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('notifications/', views.notifications, name='notifications'),

    # admin-like (requires staff)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/rooms/create/', views.create_room, name='create_room'),
    path('admin/rooms/<int:pk>/edit/', views.update_room, name='update_room'),
    path('admin/reservations/', views.list_reservations, name='list_reservations'),
    path('admin/reservations/<int:pk>/approve/', views.approve_reservation, name='approve_reservation'),
    path('admin/reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]

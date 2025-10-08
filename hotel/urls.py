from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('reserve/<int:room_id>/', views.make_reservation, name='make_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('notifications/', views.notifications, name='notifications'),
    path('admin-reservations/', views.admin_reservations, name='admin_reservations'),
    path('approve/<int:res_id>/', views.approve_reservation, name='approve_reservation'),
    path('cancel/<int:res_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    path('manage-rooms/', views.manage_rooms, name='manage_rooms'),

    # Room CRUD
    path('add-room/', views.add_room, name='add_room'),
    path('rooms/update/<int:room_id>/', views.update_room, name='update_room'),
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),

    # ✅ User management URLs
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # Custom logout
    path('logout/', views.logout_view, name='logout'),
]

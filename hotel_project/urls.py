from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom logout view (GET method accepted)
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Built-in authentication routes (login, password change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Your hotel app URLs
    path('', include('hotel.urls')),
]

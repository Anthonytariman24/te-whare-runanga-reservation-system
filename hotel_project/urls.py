from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Custom logout path FIRST (accepts GET)
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # ✅ Built-in authentication routes
    path('accounts/', include('django.contrib.auth.urls')),

    # ✅ Your main hotel app URLs LAST
    path('', include('hotel.urls')),
]

from django.urls import path
from django.conf import settings
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]

if settings.PAYMENTS_ENABLED:
    urlpatterns.append(path('payments/', views.payment_history, name='payments'))

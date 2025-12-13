from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('new/', views.booking_create, name='create'),
    path('new/<slug:course_slug>/', views.booking_create, name='create_for_course'),
    path('<int:pk>/', views.booking_detail, name='detail'),
    path('<int:pk>/cancel/', views.booking_cancel, name='cancel'),
    path('calendar/', views.availability_calendar, name='calendar'),
    path('api/slots/', views.available_slots, name='api_slots'),
]

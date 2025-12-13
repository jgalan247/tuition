from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('level/<slug:level_slug>/', views.course_list, name='by_level'),
    path('<slug:slug>/', views.course_detail, name='detail'),
    path('<slug:slug>/enroll/', views.course_enroll, name='enroll'),
]

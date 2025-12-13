from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('success/<int:payment_id>/', views.payment_success, name='success'),
    path('cancel/<int:payment_id>/', views.payment_cancel, name='cancel'),
    path('webhook/sumup/', views.sumup_webhook, name='sumup_webhook'),
    path('invoice/<int:payment_id>/', views.invoice_view, name='invoice'),
]

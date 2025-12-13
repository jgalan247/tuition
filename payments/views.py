from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import json

from .models import Payment, Invoice
from .services import SumUpService
from bookings.models import Booking


@login_required
def checkout(request, booking_id):
    """Checkout page for a booking."""
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)

    if booking.status not in ['pending']:
        messages.error(request, 'This booking has already been processed.')
        return redirect('bookings:detail', pk=booking.id)

    # Create or get existing pending payment
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        user=request.user,
        status='pending',
        defaults={
            'amount': booking.price,
            'description': f"Booking for {booking.course or 'tutoring session'} on {booking.date}",
            'receipt_email': request.user.email,
        }
    )

    if request.method == 'POST':
        # Create SumUp checkout
        sumup = SumUpService()
        checkout_data = sumup.create_checkout(payment)

        if checkout_data and 'id' in checkout_data:
            payment.sumup_checkout_id = checkout_data['id']
            payment.sumup_checkout_url = checkout_data.get('checkout_url', '')
            payment.status = 'processing'
            payment.save()

            # Redirect to SumUp checkout
            if payment.sumup_checkout_url:
                return redirect(payment.sumup_checkout_url)
            else:
                # Demo mode - go directly to success
                return redirect('payments:success', payment_id=payment.id)
        else:
            # Demo mode - go directly to success
            return redirect('payments:success', payment_id=payment.id)

    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success callback."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Verify payment with SumUp
    sumup = SumUpService()
    if payment.sumup_checkout_id and not payment.sumup_checkout_id.startswith('demo-'):
        status = sumup.get_checkout_status(payment.sumup_checkout_id)
        if status == 'PAID':
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.save()

            # Update booking status
            payment.booking.status = 'confirmed'
            payment.booking.save()

            messages.success(request, 'Payment successful! Your booking is confirmed.')
        else:
            messages.warning(request, 'Payment is being processed. We will confirm shortly.')
    else:
        # Demo mode - mark as completed
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()
        payment.booking.status = 'confirmed'
        payment.booking.save()
        messages.success(request, 'Booking confirmed!')

    return render(request, 'payments/success.html', {'payment': payment})


@login_required
def payment_cancel(request, payment_id):
    """Payment cancelled."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    payment.status = 'failed'
    payment.save()

    messages.warning(request, 'Payment was cancelled.')
    return render(request, 'payments/cancel.html', {'payment': payment})


@csrf_exempt
@require_POST
def sumup_webhook(request):
    """Handle SumUp webhook callbacks."""
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        checkout_id = data.get('id')

        if event_type == 'checkout.completed':
            # Find payment by checkout ID
            try:
                payment = Payment.objects.get(sumup_checkout_id=checkout_id)
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.sumup_transaction_id = data.get('transaction_id', '')
                payment.save()

                # Update booking
                payment.booking.status = 'confirmed'
                payment.booking.save()

            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment not found'}, status=404)

        return JsonResponse({'status': 'ok'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def invoice_view(request, payment_id):
    """View/download invoice."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Create invoice if it doesn't exist
    invoice, created = Invoice.objects.get_or_create(
        payment=payment,
        defaults={
            'billing_name': request.user.get_full_name(),
            'billing_email': request.user.email,
        }
    )

    context = {
        'invoice': invoice,
        'payment': payment,
    }
    return render(request, 'payments/invoice.html', context)

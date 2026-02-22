from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Booking, TimeSlot
from .forms import BookingForm
from courses.models import Course


@login_required
def booking_list(request):
    """List user's bookings."""
    bookings = Booking.objects.filter(student=request.user)

    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    context = {
        'bookings': bookings,
        'current_status': status,
    }
    return render(request, 'bookings/list.html', context)


@login_required
def booking_create(request, course_slug=None):
    """Create a new booking."""
    course = None
    if course_slug:
        course = get_object_or_404(Course, slug=course_slug, is_published=True)

    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            if course:
                booking.course = course
            booking.save()
            if settings.PAYMENTS_ENABLED:
                messages.success(request, 'Booking created! Please proceed to payment.')
                return redirect('payments:checkout', booking_id=booking.id)
            else:
                booking.status = 'confirmed'
                booking.save()
                messages.success(request, 'Booking confirmed!')
                return redirect('bookings:detail', pk=booking.id)
    else:
        initial = {}
        if course:
            initial['course'] = course
        form = BookingForm(user=request.user, initial=initial)

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'bookings/create.html', context)


@login_required
def booking_detail(request, pk):
    """View booking details."""
    booking = get_object_or_404(Booking, pk=pk, student=request.user)
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def booking_cancel(request, pk):
    """Cancel a booking."""
    booking = get_object_or_404(Booking, pk=pk, student=request.user)

    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:detail', pk=pk)

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        # TODO: Process refund if payment was made
        return redirect('dashboard:my_bookings')

    return render(request, 'bookings/cancel.html', {'booking': booking})


def availability_calendar(request):
    """Show availability calendar."""
    # Get available time slots
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Get existing bookings for the next 4 weeks
    start_date = timezone.now().date()
    end_date = start_date + timedelta(weeks=4)

    existing_bookings = Booking.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        status__in=['confirmed', 'pending']
    ).values('date', 'start_time')

    context = {
        'time_slots': time_slots,
        'existing_bookings': list(existing_bookings),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'bookings/calendar.html', context)


def available_slots(request):
    """API endpoint for available time slots (for HTMX)."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    day_of_week = date.weekday()

    # Get time slots for this day
    time_slots = TimeSlot.objects.filter(
        day_of_week=day_of_week,
        is_available=True
    )

    # Get booked slots for this date
    booked_times = Booking.objects.filter(
        date=date,
        status__in=['confirmed', 'pending']
    ).values_list('start_time', flat=True)

    available = []
    for slot in time_slots:
        if slot.start_time not in booked_times:
            available.append({
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
            })

    return JsonResponse({'slots': available})

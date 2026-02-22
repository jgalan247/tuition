from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from .models import Testimonial, ContactMessage
from .forms import ContactForm, ProfileForm
from courses.models import Course, Level
from bookings.models import Booking


def home(request):
    """Landing page."""
    featured_courses = Course.objects.filter(is_published=True, is_featured=True)[:3]
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    levels = Level.objects.all()

    context = {
        'featured_courses': featured_courses,
        'testimonials': testimonials,
        'levels': levels,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page with tutor credentials."""
    return render(request, 'core/about.html')


def pricing(request):
    """Pricing page."""
    levels = Level.objects.all()
    courses = Course.objects.filter(is_published=True)

    context = {
        'levels': levels,
        'courses': courses,
    }
    return render(request, 'core/pricing.html', context)


def contact(request):
    """Contact form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact_success')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


def contact_success(request):
    """Contact success page."""
    return render(request, 'core/contact_success.html')


@login_required
def dashboard(request):
    """Student dashboard."""
    upcoming_bookings = Booking.objects.filter(
        student=request.user,
        status__in=['confirmed', 'pending']
    ).order_by('date', 'start_time')[:5]

    recent_bookings = Booking.objects.filter(
        student=request.user,
        status='completed'
    ).order_by('-date')[:5]

    context = {
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def profile(request):
    """User profile page."""
    return render(request, 'dashboard/profile.html')


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'dashboard/profile_edit.html', {'form': form})


@login_required
def my_courses(request):
    """Student's enrolled courses."""
    # Get courses from bookings
    course_ids = Booking.objects.filter(
        student=request.user
    ).values_list('course_id', flat=True).distinct()

    courses = Course.objects.filter(id__in=course_ids)

    return render(request, 'dashboard/my_courses.html', {'courses': courses})


@login_required
def my_bookings(request):
    """Student's bookings."""
    bookings = Booking.objects.filter(student=request.user)

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    context = {
        'bookings': bookings,
        'current_status': status,
    }
    return render(request, 'dashboard/my_bookings.html', context)


@login_required
def payment_history(request):
    """Payment history."""
    if not settings.PAYMENTS_ENABLED:
        return redirect('dashboard:home')
    from payments.models import Payment
    payments = Payment.objects.filter(user=request.user)

    return render(request, 'dashboard/payments.html', {'payments': payments})

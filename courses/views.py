from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Course, Level, Subject, Topic


def course_list(request, level_slug=None):
    """List all courses, optionally filtered by level."""
    courses = Course.objects.filter(is_published=True)
    levels = Level.objects.all()
    current_level = None

    if level_slug:
        current_level = get_object_or_404(Level, slug=level_slug)
        courses = courses.filter(level=current_level)

    # Search functionality
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query)
        )

    context = {
        'courses': courses,
        'levels': levels,
        'current_level': current_level,
        'query': query,
    }
    return render(request, 'courses/list.html', context)


def course_detail(request, slug):
    """Course detail page."""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    topics = course.topics.prefetch_related('lessons')

    # Related courses
    related_courses = Course.objects.filter(
        is_published=True,
        subject=course.subject
    ).exclude(id=course.id)[:3]

    context = {
        'course': course,
        'topics': topics,
        'related_courses': related_courses,
    }
    return render(request, 'courses/detail.html', context)


@login_required
def course_enroll(request, slug):
    """Redirect to booking for this course."""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    messages.info(request, f'Book a session for {course.title}')
    return redirect('bookings:create_for_course', course_slug=slug)

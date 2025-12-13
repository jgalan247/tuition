from django.db import models
from django.conf import settings
from django.utils import timezone


class TimeSlot(models.Model):
    """Available time slots for booking."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    # For face-to-face sessions
    max_students = models.PositiveSmallIntegerField(default=3)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Booking(models.Model):
    """A booking for a tutoring session."""

    class SessionType(models.TextChoices):
        ONE_TO_ONE = 'one_to_one', '1-to-1 (£60/hr)'
        TWO_STUDENTS = 'two_students', '2 Students (£100/hr)'
        THREE_STUDENTS = 'three_students', '3 Students (£120/hr)'

    class DeliveryMode(models.TextChoices):
        ONLINE = 'online', 'Online'
        FACE_TO_FACE = 'face_to_face', 'Face-to-Face'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Payment'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'

    # Who
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    additional_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='group_bookings',
        help_text='Additional students for group sessions'
    )

    # What
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Specific topic to cover'
    )
    notes = models.TextField(blank=True, help_text='Any specific topics or questions')

    # When
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)

    # How
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.ONE_TO_ONE
    )
    delivery_mode = models.CharField(
        max_length=20,
        choices=DeliveryMode.choices,
        default=DeliveryMode.ONLINE
    )

    # Meeting details
    meeting_link = models.URLField(blank=True, help_text='Zoom/Google Meet link for online sessions')
    location = models.CharField(max_length=200, blank=True, help_text='Address for face-to-face sessions')

    # Pricing (in pence)
    price = models.PositiveIntegerField(help_text='Price in pence')

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.student} - {self.date} {self.start_time.strftime('%H:%M')}"

    @property
    def price_display(self):
        """Return price in pounds."""
        return f"£{self.price / 100:.2f}"

    @property
    def is_upcoming(self):
        """Check if booking is in the future."""
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        return booking_datetime > now

    @property
    def total_students(self):
        """Total number of students in this session."""
        return 1 + self.additional_students.count()

    def calculate_price(self):
        """Calculate price based on session type and duration."""
        base_prices = settings.PRICING
        base_price = base_prices.get(self.session_type, base_prices['one_to_one'])
        return int(base_price * float(self.duration_hours))

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.calculate_price()
        super().save(*args, **kwargs)


class BookingNote(models.Model):
    """Notes and feedback for completed sessions."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='session_note')

    # Tutor's notes
    topics_covered = models.TextField(help_text='What was covered in the session')
    homework = models.TextField(blank=True, help_text='Homework or practice exercises')
    next_session = models.TextField(blank=True, help_text='Topics for next session')

    # Student feedback
    student_feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.booking}"

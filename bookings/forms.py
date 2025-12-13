from django import forms
from django.conf import settings
from .models import Booking
from courses.models import Course


class BookingForm(forms.ModelForm):
    """Booking creation form."""

    class Meta:
        model = Booking
        fields = [
            'course', 'topic', 'session_type', 'delivery_mode',
            'date', 'start_time', 'duration_hours', 'notes'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'delivery_mode': forms.RadioSelect(),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'min': ''  # Will be set in __init__
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time'
            }),
            'duration_hours': forms.Select(
                choices=[
                    (1.0, '1 hour'),
                    (1.5, '1.5 hours'),
                    (2.0, '2 hours'),
                ],
                attrs={'class': 'form-select'}
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Any specific topics or questions you want to cover...'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Set minimum date to today
        from django.utils import timezone
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()

        # Filter courses to published only
        self.fields['course'].queryset = Course.objects.filter(is_published=True)
        self.fields['course'].required = False
        self.fields['topic'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration_hours')

        if date and start_time and duration:
            from datetime import datetime, timedelta
            start_datetime = datetime.combine(date, start_time)
            end_time = (start_datetime + timedelta(hours=float(duration))).time()
            cleaned_data['end_time'] = end_time

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)

        # Set end time
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(booking.date, booking.start_time)
        booking.end_time = (start_datetime + timedelta(hours=float(booking.duration_hours))).time()

        # Calculate price
        booking.price = booking.calculate_price()

        if commit:
            booking.save()
        return booking


class BookingFilterForm(forms.Form):
    """Form for filtering bookings."""

    STATUS_CHOICES = [('', 'All')] + list(Booking.Status.choices)

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from bookings.models import TimeSlot
from datetime import time


class Command(BaseCommand):
    help = 'Set up initial data for TuitionHub'

    def handle(self, *args, **options):
        # Update site
        site, created = Site.objects.get_or_create(pk=1)
        site.domain = 'tuitionhub.co.uk'
        site.name = 'TuitionHub'
        site.save()
        self.stdout.write(self.style.SUCCESS(f'Site updated: {site.domain}'))

        # Create time slots (weekday evenings and weekends)
        slots_created = 0

        # Weekday slots (Monday to Friday: 16:00-21:00)
        for day in range(5):  # 0-4 is Monday-Friday
            for hour in range(16, 21):  # 4pm to 8pm (last slot starts at 8pm)
                slot, created = TimeSlot.objects.get_or_create(
                    day_of_week=day,
                    start_time=time(hour, 0),
                    defaults={
                        'end_time': time(hour + 1, 0),
                        'is_available': True,
                        'max_students': 3
                    }
                )
                if created:
                    slots_created += 1

        # Weekend slots (Saturday and Sunday: 9:00-18:00)
        for day in [5, 6]:  # 5=Saturday, 6=Sunday
            for hour in range(9, 18):  # 9am to 5pm
                slot, created = TimeSlot.objects.get_or_create(
                    day_of_week=day,
                    start_time=time(hour, 0),
                    defaults={
                        'end_time': time(hour + 1, 0),
                        'is_available': True,
                        'max_students': 3
                    }
                )
                if created:
                    slots_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {slots_created} time slots'))

        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))

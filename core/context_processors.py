from django.conf import settings


def site_settings(request):
    """Add site settings to template context."""
    return {
        'SITE_NAME': 'TuitionHub',
        'SITE_TAGLINE': 'Expert Computer Science Tuition',
        'TUTOR_NAME': 'Dr. [Your Name]',
        'TUTOR_CREDENTIALS': 'PhD Computer Science (Queen Mary University of London)',
        'TUTOR_EXPERIENCE': '15+ years teaching experience, OCR Examiner',
        'CONTACT_EMAIL': 'info@tuitionhub.co.uk',
        'CONTACT_PHONE': '+44 XXXX XXXXXX',
        'PRICING': {
            'one_to_one': 60,
            'two_students': 100,
            'three_students': 120,
        },
        'DEBUG': settings.DEBUG,
        'PAYMENTS_ENABLED': settings.PAYMENTS_ENABLED,
    }

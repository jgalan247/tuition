from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('courses/', include('courses.urls')),
    path('bookings/', include('bookings.urls')),
    path('dashboard/', include('core.urls_dashboard')),
    path('', include('core.urls')),
]

if settings.PAYMENTS_ENABLED:
    urlpatterns.insert(4, path('payments/', include('payments.urls')))

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

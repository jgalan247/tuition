from django.contrib import admin
from .models import TimeSlot, Booking, BookingNote


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'is_available', 'max_students')
    list_filter = ('day_of_week', 'is_available')
    list_editable = ('is_available',)
    ordering = ('day_of_week', 'start_time')


class BookingNoteInline(admin.StackedInline):
    model = BookingNote
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'date', 'start_time',
        'session_type', 'delivery_mode', 'status', 'price_display'
    )
    list_filter = ('status', 'session_type', 'delivery_mode', 'date', 'course')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'price_display')
    inlines = [BookingNoteInline]

    fieldsets = (
        ('Student', {
            'fields': ('student', 'additional_students')
        }),
        ('Session Details', {
            'fields': ('course', 'topic', 'session_type', 'delivery_mode', 'notes')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Meeting', {
            'fields': ('meeting_link', 'location')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'price_display', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Mark selected bookings as confirmed"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected bookings as completed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Mark selected bookings as cancelled"


@admin.register(BookingNote)
class BookingNoteAdmin(admin.ModelAdmin):
    list_display = ('booking', 'created_at')
    search_fields = ('booking__student__email', 'topics_covered', 'homework')

from django.contrib import admin
from .models import Level, Subject, Course, Topic, Lesson, Resource, StudentProgress


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'subject', 'delivery_mode', 'is_published', 'is_featured')
    list_filter = ('level', 'subject', 'is_published', 'is_featured', 'delivery_mode')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    list_editable = ('is_published', 'is_featured')
    inlines = [TopicInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'subject', 'level')
        }),
        ('Content', {
            'fields': ('description', 'learning_outcomes', 'prerequisites', 'syllabus_reference')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('delivery_mode', 'duration_weeks', 'is_published', 'is_featured')
        }),
    )


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'spec_reference')
    list_filter = ('course__level', 'course')
    search_fields = ('title', 'description', 'spec_reference')
    inlines = [LessonInline]


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order', 'duration_minutes')
    list_filter = ('topic__course__level', 'topic__course')
    search_fields = ('title', 'description', 'content')
    inlines = [ResourceInline]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'resource_type')
    list_filter = ('resource_type',)
    search_fields = ('title', 'description')


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'course')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

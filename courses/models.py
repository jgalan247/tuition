from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Level(models.Model):
    """Educational level (KS3, GCSE, A-Level)."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subject(models.Model):
    """Subject area (Computer Science, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    image = models.ImageField(upload_to='subjects/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """A course offering (e.g., A-Level Computer Science)."""

    class DeliveryMode(models.TextChoices):
        ONLINE = 'online', 'Online'
        FACE_TO_FACE = 'face_to_face', 'Face-to-Face'
        BOTH = 'both', 'Both'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses')

    # Content
    description = models.TextField()
    learning_outcomes = models.TextField(blank=True, help_text="What students will learn")
    prerequisites = models.TextField(blank=True, help_text="Required prior knowledge")
    syllabus_reference = models.CharField(max_length=100, blank=True, help_text="e.g., OCR H446")

    # Media
    image = models.ImageField(upload_to='courses/', blank=True, null=True)

    # Settings
    delivery_mode = models.CharField(
        max_length=20,
        choices=DeliveryMode.choices,
        default=DeliveryMode.BOTH
    )
    duration_weeks = models.PositiveSmallIntegerField(default=12)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level__order', 'title']
        unique_together = ['subject', 'level']

    def __str__(self):
        return f"{self.level.name} {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.level.name}-{self.title}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})


class Topic(models.Model):
    """A topic/module within a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    # OCR specification reference
    spec_reference = models.CharField(max_length=50, blank=True, help_text="e.g., 1.1.1")

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lesson within a topic."""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Lesson content in markdown")
    order = models.PositiveSmallIntegerField(default=0)

    # Duration in minutes
    duration_minutes = models.PositiveSmallIntegerField(default=60)

    # Resources
    video_url = models.URLField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class Resource(models.Model):
    """Downloadable resources for lessons."""

    class ResourceType(models.TextChoices):
        PDF = 'pdf', 'PDF Document'
        VIDEO = 'video', 'Video'
        CODE = 'code', 'Code Example'
        EXERCISE = 'exercise', 'Exercise'
        SOLUTION = 'solution', 'Solution'
        LINK = 'link', 'External Link'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class StudentProgress(models.Model):
    """Track student progress through courses."""

    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name_plural = 'Student progress'

    def __str__(self):
        return f"{self.user} - {self.lesson}"

from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="#6366f1")
    progress = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )
    session_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.duration} minutes"
from django.contrib import admin
from .models import Subject, Task, Note, StudySession


admin.site.register(Subject)
admin.site.register(Task)
admin.site.register(Note)
admin.site.register(StudySession)
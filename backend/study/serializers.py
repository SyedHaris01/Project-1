from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Note, StudySession, Subject, Task


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "description",
            "color",
            "progress",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_progress(self, progress):
        if not 0 <= progress <= 100:
            raise serializers.ValidationError("Progress must be between 0 and 100.")
        return progress


class TaskSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "due_date", "priority", "completed", "subject", "subject_name", "created_at"]
        read_only_fields = ["id", "created_at", "subject_name"]

    def validate_subject(self, subject):
        request = self.context.get("request")
        if subject and request and subject.user_id != request.user.id:
            raise serializers.ValidationError("You cannot use this subject.")
        return subject


class NoteSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Note
        fields = ["id", "title", "content", "subject", "subject_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "subject_name"]

    def validate_subject(self, subject):
        request = self.context.get("request")
        if subject and request and subject.user_id != request.user.id:
            raise serializers.ValidationError("You cannot use this subject.")
        return subject


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ["id", "duration", "subject", "session_date"]
        read_only_fields = ["id", "session_date"]

    def validate_duration(self, duration):
        if duration < 1:
            raise serializers.ValidationError("Duration must be at least one minute.")
        return duration

    def validate_subject(self, subject):
        request = self.context.get("request")
        if subject and request and subject.user_id != request.user.id:
            raise serializers.ValidationError("You cannot use this subject.")
        return subject
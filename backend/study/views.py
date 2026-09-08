from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Note, StudySession, Subject, Task
from .serializers import (NoteSerializer, RegisterSerializer,
                          StudySessionSerializer, SubjectSerializer,
                          TaskSerializer, UserSerializer)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


class CurrentUserAPIView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=400)
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "study/register.html",
                {"error": "Passwords do not match."}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "study/register.html",
                {"error": "Username already exists."}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "study/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "study/login.html",
            {"error": "Invalid username or password."}
        )

    return render(request, "study/login.html")


@login_required
def dashboard(request):
    return render(request, "study/dashboard.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


class SubjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)


class UserOwnedViewSetMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(UserOwnedViewSetMixin, generics.ListCreateAPIView):
    model = Task
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related("subject")
        status_filter = self.request.query_params.get("status")
        if status_filter == "pending":
            queryset = queryset.filter(completed=False)
        elif status_filter == "completed":
            queryset = queryset.filter(completed=True)
        return queryset


class TaskDetailAPIView(UserOwnedViewSetMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Task
    serializer_class = TaskSerializer


class NoteViewSet(UserOwnedViewSetMixin, generics.ListCreateAPIView):
    model = Note
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related("subject")
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(content__icontains=search)
        return queryset.order_by("-updated_at")


class NoteDetailAPIView(UserOwnedViewSetMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Note
    serializer_class = NoteSerializer


class StudySessionViewSet(UserOwnedViewSetMixin, generics.ListCreateAPIView):
    model = StudySession
    serializer_class = StudySessionSerializer


class StudySessionDetailAPIView(UserOwnedViewSetMixin, generics.RetrieveUpdateDestroyAPIView):
    model = StudySession
    serializer_class = StudySessionSerializer


class DashboardAPIView(APIView):
    def get(self, request):
        user = request.user
        today = timezone.localdate()
        week_start = today - timedelta(days=6)
        sessions = StudySession.objects.filter(user=user, session_date__date__gte=week_start)
        weekly_progress = [
            {
                "date": (week_start + timedelta(days=offset)).isoformat(),
                "minutes": sum(
                    item.duration
                    for item in sessions
                    if item.session_date.date() == week_start + timedelta(days=offset)
                ),
            }
            for offset in range(7)
        ]
        completed_tasks = Task.objects.filter(user=user, completed=True).count()
        return Response({
            "subjects": Subject.objects.filter(user=user).count(),
            "pending_tasks": Task.objects.filter(user=user, completed=False).count(),
            "notes": Note.objects.filter(user=user).count(),
            "study_hours": round((StudySession.objects.filter(user=user).aggregate(total=Sum("duration"))["total"] or 0) / 60, 1),
            "today_tasks": TaskSerializer(Task.objects.filter(user=user, due_date=today).select_related("subject"), many=True).data,
            "recent_notes": NoteSerializer(Note.objects.filter(user=user).select_related("subject").order_by("-updated_at")[:5], many=True).data,
            "weekly_minutes": sum(item.duration for item in sessions),
            "completed_tasks": completed_tasks,
            "weekly_progress": weekly_progress,
            "recent_sessions": StudySessionSerializer(
                StudySession.objects.filter(user=user).select_related("subject").order_by("-session_date")[:5],
                many=True,
            ).data,
        })


class ProgressAPIView(APIView):
    def get(self, request):
        user = request.user
        subjects = Subject.objects.filter(user=user)
        return Response({
            "study_hours": round((StudySession.objects.filter(user=user).aggregate(total=Sum("duration"))["total"] or 0) / 60, 1),
            "completed_tasks": Task.objects.filter(user=user, completed=True).count(),
            "subjects": [
                {
                    "id": subject.id,
                    "name": subject.name,
                    "color": subject.color,
                    "minutes": StudySession.objects.filter(user=user, subject=subject).aggregate(total=Sum("duration"))["total"] or 0,
                    "progress": subject.progress,
                }
                for subject in subjects
            ],
        })
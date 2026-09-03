from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Subject
from .serializers import RegisterSerializer, SubjectSerializer, UserSerializer


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
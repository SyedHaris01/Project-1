from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    path("api/subjects/", views.SubjectListCreateAPIView.as_view(), name="subject-list"),
    path("api/subjects/<int:pk>/", views.SubjectDetailAPIView.as_view(), name="subject-detail"),
    path("api/auth/register/", views.RegisterAPIView.as_view(), name="api-register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="api-login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="api-refresh"),
    path("api/auth/me/", views.CurrentUserAPIView.as_view(), name="api-me"),
    path("api/auth/logout/", views.LogoutAPIView.as_view(), name="api-logout"),
    path("api/dashboard/", views.DashboardAPIView.as_view(), name="api-dashboard"),
    path("api/progress/", views.ProgressAPIView.as_view(), name="api-progress"),
    path("api/tasks/", views.TaskViewSet.as_view(), name="task-list"),
    path("api/tasks/<int:pk>/", views.TaskDetailAPIView.as_view(), name="task-detail"),
    path("api/notes/", views.NoteViewSet.as_view(), name="note-list"),
    path("api/notes/<int:pk>/", views.NoteDetailAPIView.as_view(), name="note-detail"),
    path("api/sessions/", views.StudySessionViewSet.as_view(), name="session-list"),
    path("api/sessions/<int:pk>/", views.StudySessionDetailAPIView.as_view(), name="session-detail"),
]
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Subject, Task


class StudyApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="owner", password="password123")
		self.other_user = User.objects.create_user(username="other", password="password123")
		self.client.force_authenticate(self.user)

	def test_subjects_are_private_and_tasks_validate_subject_owner(self):
		own_subject = Subject.objects.create(user=self.user, name="Physics")
		other_subject = Subject.objects.create(user=self.other_user, name="History")

		response = self.client.get(reverse("subject-list"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual([item["id"] for item in response.data], [own_subject.id])

		response = self.client.post(reverse("task-list"), {
			"title": "Review vectors",
			"subject": other_subject.id,
		}, format="json")
		self.assertEqual(response.status_code, 400)
		self.assertEqual(Task.objects.count(), 0)

	def test_dashboard_and_progress_return_real_user_data(self):
		Subject.objects.create(user=self.user, name="Physics", progress=40)
		Task.objects.create(user=self.user, title="Read chapter", completed=True)

		dashboard = self.client.get(reverse("api-dashboard"))
		progress = self.client.get(reverse("api-progress"))

		self.assertEqual(dashboard.status_code, 200)
		self.assertEqual(dashboard.data["subjects"], 1)
		self.assertEqual(dashboard.data["completed_tasks"], 1)
		self.assertEqual(len(dashboard.data["weekly_progress"]), 7)
		self.assertEqual(progress.status_code, 200)
		self.assertEqual(progress.data["completed_tasks"], 1)

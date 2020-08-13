from django.test import TestCase
from .models import Task

class TaskModelTests(TestCase):
    def test_completed_task(self):

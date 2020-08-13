import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    task_text = models.CharField(max_length=200, verbose_name='Description')
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True)
    _completed = models.BooleanField(default=False)

    id = models.AutoField(primary_key=True)
    def __str__(self):
      return self.task_text

    @property 
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        print("completed setter")
        self._completed = value
        if(value):
            print("setting date completed")
            self.date_completed = timezone.now()
            print(timezone.now())

    def was_created_recently(self):
      return self.date_created >= timezone.now() - datetime.timedelta(days=1)
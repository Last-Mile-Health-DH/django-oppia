from django.db import models
from django.contrib.auth.models import User
from oppia.models.cohorts import Cohort
from oppia.models.main import Course

# Create your models here.

class TrainingStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELED = 'canceled', 'Canceled'

class TrainingTypeChoices(models.TextChoices):
    LEARNER = 'learner', 'Learner'
    INSTRUCTOR = 'instructor', 'Instructor'


class ModuleType(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=100)
   description = models.TextField(null=True, blank=True)
   code = models.CharField(max_length=50, unique=True, null=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   def __str__(self):
       return self.name

class Training(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateField()
    sponsor = models.CharField(max_length=255, null=True, blank=True)
    module_type = models.ForeignKey(ModuleType, on_delete=models.CASCADE, related_name='trainings')
    status = models.CharField(max_length=50, choices=TrainingStatus.choices, default=TrainingStatus.SCHEDULED)
    users = models.ManyToManyField(User, related_name='trainings', blank=True)
    training_type = models.CharField(max_length=50, choices=TrainingTypeChoices.choices, default=TrainingTypeChoices.LEARNER)
    training_center = models.CharField(max_length=255, null=True, blank=True)
    cohorts = models.ManyToManyField(Cohort, related_name='trainings', blank=True)
    courses = models.ManyToManyField(Course, related_name='trainings', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.date}"
    
    # Method to get all users associated with this training
    def get_participants(self):
        return self.users.all()
    
    
    


from django.db import models
from ATskills.models import SUBJECT_CHOICES, Skill, Task, User
# Create your models here.

class MISTAKE_TYPE_CHOICES(models.IntegerChoices):
    _ = 1, ' '

class Mistake(models.Model):
    user = models.ForeignKey(User)
    mistake_type = models.IntegerChoices(choices = MISTAKE_TYPE_CHOICES)
    task = models.ForeignKey(Task)
    # skills = models.ManyToManyField(Skill, blank = True) 
    fine = models.IntegerField(null=True, blank = True)
    tip = models.TextField(null=True, blank = True)
    is_tip_shown = models.BooleanField(default=False)

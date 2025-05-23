from django.db import models

from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User

# Create your models here.


class MISTAKE_TYPE_CHOICES(models.IntegerChoices):
    SYNTAX = 1, " "
    LOGIC = 2, " "
    LEXIC = 3, " "


class Mistake(models.Model):
    user = models.ForeignKey(User, to_field="user_id", on_delete=models.CASCADE)
    mistake_type = models.IntegerField(choices=MISTAKE_TYPE_CHOICES)
    task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, blank=True)
    fine = models.FloatField(null=True, blank=True)
    tip = models.TextField(null=True, blank=True)
    is_tip_shown = models.BooleanField(default=False)

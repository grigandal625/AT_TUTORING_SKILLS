from django.db import models

from ATskills.models import Task, User

# Create your models here.


class MISTAKE_TYPE_CHOICES(models.IntegerChoices):
    _ = 1, " "


class Mistake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mistake_type = models.IntegerField(choices=MISTAKE_TYPE_CHOICES)
    task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)
    # skills = models.ManyToManyField(Skill, blank = True)
    fine = models.IntegerField(null=True, blank=True)
    tip = models.TextField(null=True, blank=True)
    is_tip_shown = models.BooleanField(default=False)

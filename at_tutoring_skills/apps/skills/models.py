from django.db import models

# Create your models here.


class SUBJECT_CHOICES(models.IntegerChoices):
    KB_TYPE = 1, "Тип"
    KB_OBJECT = 2, "Объект"
    KB_EVENT = 3, "Событие"
    KB_INTERVAL = 4, "Интервал"
    KB_RULE = 5, "Правило"
    SIMULATION_RESOURCE_TYPES = 6, "Тип ресурса"
    SIMULATION_RESOURCES = 7, "Ресурс"
    SIMULATION_TEMPLATES = 8, "Образец операции"
    SIMULATION_TEMPLATE_USAGES = 9, "Операции"
    SIMULATION_FUNCS = 10, "Функция"


class GROUP_CHOICES(models.IntegerChoices):
    KB = 1, "KB"
    SIMULATION = 2, "SIMULATION"


class Skill(models.Model):
    name = models.CharField(max_length=255)  # Название умения
    group = models.IntegerField(choices=GROUP_CHOICES)
    code = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    task_name = models.CharField(max_length=255)  # Название события
    task_object = models.IntegerField(choices=SUBJECT_CHOICES)
    object_name = models.CharField(max_length=255)  # заполняшка от параметров
    description = models.TextField()  # Описание задания

    object_reference = models.JSONField(null=True, blank=True)  # Параметры события (JSON или пустые)

    skills = models.ManyToManyField(
        Skill, related_name="tasks_skills", default=None
    )  # Связь "многие-ко-многим" с умениями


class Variant(models.Model):
    name = models.CharField(max_length=255, default=None)  # проблемная область/название
    task = models.ManyToManyField(Task)


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=255)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True, default=None)


class TaskUser(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, to_field="user_id", on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)


class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    mark = models.FloatField(default=100)
    is_completed = models.BooleanField(default=False)

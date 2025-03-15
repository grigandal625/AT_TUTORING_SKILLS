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
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  # Название умения
    group = models.IntegerField(choices=GROUP_CHOICES)


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    variant = models.IntegerField()


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255)  # Название события
    task_object = models.IntegerField(choices=SUBJECT_CHOICES)
    object_name = models.CharField(max_length=255)  # заполняшка от параметров
    description = models.TextField()  # Описание задания

    object_reference = models.JSONField(null=True, blank=True)  # Параметры события (JSON или пустые)

    skills = models.ManyToManyField(Skill, related_name="tasks_skills")  # Связь "многие-ко-многим" с умениями


class Task_User(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)


class User_Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

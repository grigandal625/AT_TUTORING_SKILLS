from django.db import models

# Create your models here.


class Skill(models.Model):
    name = models.CharField(max_length=255)  # Название умения
    # tasks_ids = models.ArrayField(models.IntegerField(), blank=True, default=list)  # Список связанных заданий
    scenario_name = models.CharField(max_length=255, null=True, blank=True)  # Название сценария (может быть пустым)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    task_name = models.CharField(max_length=255)  # Название события
    description = models.TextField()  # Описание задания
    event_params =  models.JSONField(null=True, blank=True) # Параметры события (JSON или пустые)
    on_success = models.IntegerField()  # Баллы за успешное выполнение
    on_failure = models.IntegerField()  # Штрафные баллы за неуспешное выполнение
    skills = models.ManyToManyField(Skill, related_name='tasks')  # Связь "многие-ко-многим" с умениями

    def __str__(self):
        return self.event_name


class Reaction(models.Model):
    task = models.ForeignKey(
        'Task',  # Ссылка на модель Task
        on_delete=models.CASCADE,  # Удалять реакции, если удаляется задание
        related_name='reactions'  # Имя обратной связи для доступа из Task
    )
    message = models.TextField()  # Сообщение реакции

    def __str__(self):
        return f"Scenario: {self.scenario_name}, Task: {self.task.id}, Status: {self.status}"

class ScenarioPart(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('DONE', 'Done'),
        ('IN_PROGRESS', 'In Progress'),
    ]

    scenario_name = models.CharField(max_length=255)  # Название сценария
    task = models.ForeignKey(
        'Task',  # Ссылка на модель Task
        on_delete=models.CASCADE,  # Удалять ScenarioPart, если удаляется связанное задание
        related_name='scenario_parts'  # Имя обратной связи для Task
    )
    parent_tasks = models.ManyToManyField(
        'self',  # Связь с самой собой
        symmetrical=False,  # Родитель может быть один или несколько
        related_name='child_tasks',  # Имя обратной связи для дочерних задач
        blank=True  # Может быть пустым
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='TODO'  # Значение по умолчанию
    )

    def __str__(self):
        return f"Scenario: {self.scenario_name}, Task: {self.task.id}, Status: {self.status}"
    
class Event(models.Model):
    OPERATION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('GET', 'Get'),
        ('TRANSLATE', 'Translate'),
        ('IMPORT', 'Import'),
        ('EXPORT', 'Export'),
        ('COMPUTE', 'Compute'),
    ]

    OPERANDS = [
        ('NIL', 'Nil'),
        ('MODEL', 'Model'),
        ('RESOURCE_TYPE', 'Resource Type'),
        ('RESOURCE', 'Resource'),
        ('FUNCTION', 'Function'),
        ('TEMPLATE', 'Template'),
        ('TEMPLATE_USAGE', 'Template Usage'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('ERROR', 'Error'),
    ]

    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPES,
        default='GET'
    )  # Тип операции
    operand = models.CharField(
        max_length=50,
        choices=OPERANDS,
        default='NIL',
        blank=True
    )  # Операнд
    params = models.JSONField()  # Параметры в формате JSON
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SUCCESS'
    )  # Статус
    error_code = models.IntegerField(
        null=True,
        blank=True
    )  # Код ошибки (если есть)
    error_message = models.TextField(
        blank=True
    )  # Сообщение об ошибке
    is_scenario = models.BooleanField(default=False)  # Является ли частью сценария

    def __str__(self):
        return f"Event: {self.operation_type}, Operand: {self.operand}, Status: {self.status}"

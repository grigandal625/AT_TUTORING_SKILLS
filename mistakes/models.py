from django.db import models
from ATskills.models import Skill, Task
# Create your models here.


class Mistake(models.Model):
    class MistakeTypeChoises(models.IntegerChoices):
        CODE_1 = 1, 'Лексическая'
        CODE_2 = 2, 'Синтаксическая'
        CODE_3 = 3, 'Логическая'

    class MistakeRootContextChoises(models.IntegerChoices):
        TYPE = 1, 'Тип'
        OBJECT = 2, 'Объект'
        EVENT = 3, 'Событие'
        INTERVAL = 4, 'Интервалл'
        RULE = 5, 'Правило'
        RESOURCE_TYPES = 6, 'Тип ресурса'
        RESOURCES = 7, 'Ресурс'
        TEMPLATES = 8, 'Образец операции'
        TEMPLATE_USAGES = 9, 'Операции'
        FUNCS = 10, 'Функция'

    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank = True)
    skills = models.ManyToManyField(Skill, blank = True)
    fine = models.IntegerField(null=True, blank = True)
    codificator1 = models.IntegerField(
        choices=MistakeTypeChoises.choices,
        null=True,
        blank=True
    )
    root_context = models.IntegerField(
        choices=MistakeRootContextChoises.choices,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Mistake: Task {self.id_task}, Fine {self.fine}, Codificator {self.codificator1}"
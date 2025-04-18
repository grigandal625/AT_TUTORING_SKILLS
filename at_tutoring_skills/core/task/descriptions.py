from at_tutoring_skills.apps.skills.models import Task, SUBJECT_CHOICES

from at_krl.models.kb_type import KBNumericTypeModel, KBSymbolicTypeModel, KBFuzzyTypeModel
from at_krl.models.kb_entity import KBRootModel
from at_krl.models.kb_class import KBClassModel
from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.utils.context import Context

from at_krl.core.kb_entity import KBEntity
from at_krl.core.kb_type import KBType, KBNumericType, KBSymbolicType, KBFuzzyType
from at_krl.core.kb_rule import KBRule
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from at_krl.core.kb_class import KBClass



class KBTypeRootModel(KBRootModel[KBNumericTypeModel | KBSymbolicTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context)

class DescriptionsService:

    KB_SUBJECT_TO_MODEL = {
        SUBJECT_CHOICES.KB_TYPE: KBTypeRootModel,
        SUBJECT_CHOICES.KB_OBJECT: KBClassModel,
        SUBJECT_CHOICES.KB_RULE: KBRuleModel,
        SUBJECT_CHOICES.KB_EVENT: KBEventModel,
        SUBJECT_CHOICES.KB_INTERVAL: KBIntervalModel,
    }

    def get_kb_task_description(self, task: Task):
        entity = self.get_kb_task_entity(task)
        return self.get_kb_entity_description(entity)

    def get_kb_task_entity(self, task: Task):
        ctx = Context(name="generate_description")
        model = self.KB_SUBJECT_TO_MODEL[task.task_object](**task.object_reference)
        return model.to_internal(context=ctx)

    def get_kb_entity_description(self, entity: KBEntity):
        if isinstance(entity, KBType):
            return self.get_kb_type_descritpion(entity)
        elif isinstance(entity, KBEvent):
            return self.get_kb_event_descritpion(entity)
        elif isinstance(entity, KBInterval):
            return self.get_kb_interval_descritpion(entity)
        elif isinstance(entity, KBClass):
            return self.get_kb_class_descritpion(entity)
        elif isinstance(entity, KBRule):
            return self.get_kb_rule_descritpion(entity)
        else:
            raise ValueError("Unknown kb entity type to generate desctription for")

    def get_kb_type_descritpion(self, type: KBType):
        if isinstance(type, KBNumericType):
            return f'''\n    Числовой тип, определяющий значения от {type.from_} до {type.to_}'''
        elif isinstance(type, KBSymbolicType):
            values = ", ".join(type.values)
            return f'''\n    Символьный тип, определяющий набор символьных значений: {values}'''
        elif isinstance(type, KBFuzzyType):
            mf_values = ", ".join([f.name for f in type.membership_functions])
            return f'''\n    Нечеткий тип, определяющий лингвистическую переменную "{type.id}" с функциями принадлежности для значений: {mf_values}'''
        else:
            raise ValueError("Unknown kb type to generate desctription for")


    def get_kb_event_descritpion(self, event: KBEvent):
        return f'''\n    Событие, с условием возникновения

        {event.occurance_condition.krl}
        '''

    def get_kb_interval_descritpion(self, interval: KBInterval):
        return f'''\n    Интервал, с условием начала 

        {interval.open.krl}

    и условием окончания

        {interval.close.krl}'''

    def get_kb_class_descritpion(self, class_: KBClass):
        attributes = "\n"
        for prop in class_.properties:
            attributes += f'        - Атрибут "{prop.id}" типа "{prop.type.id}"\n'
        return f'''\n\n    Базовый объект с набором атрибутов: \n{attributes}'''

    def get_kb_rule_descritpion(self, rule: KBRule):
        result = f'''
    
    Правило с условием

        {rule.condition.krl}

    набором действий при истинности условия:
        '''

        for instruction in rule.instructions:
            result += f'\n        - {instruction.krl}'

        if rule.else_instructions:
            result += f'\n\n    и набором действий при ложности условия:'
            for instruction in rule.else_instructions:
                result += f'\n\n        - {instruction.krl}'
        return result

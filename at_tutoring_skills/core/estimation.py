from at_tutoring_skills.core import copmarison
from dataclasses import dataclass, field
from typing import List
from at_krl.core.kb_type import KBType, KBFuzzyType, KBNumericType, KBSymbolicType
from at_krl.core.kb_class import KBClass
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
# from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_rule import KBRule


@dataclass(kw_only=True)
class Context:
    parent: "Context" = field(default=None, repr=False)
    name: str

    def create_child(self, name):
        return Context(parent=self, name=name)
    
    @property
    def full_path_list(self) -> List[str]:
        return self.parent.full_path_list + [self.name] if self.parent else [self.name]
    
class StudentMistakeException(Exception):
    context: Context

    def __init__(self, msg, context: Context, *args):
        super().__init__(msg, *args)
        self.context = context

# def estimate_kb(kb):
#     kb_context = Context('KB')
    
    # for r in kb.rules:
    #     try:
    #         estimate_rule(r, context=kb_context.create_child('rules').create_child(r.name))
    #     except StudentMistakeException as e:
    #         return {
    #             'error': True,
    #             'stage_done': False,
    #             'mistake': str(e),
    #             'mistake_path': e.context.full_path_list
    #         }

def estimate_string_type(type_et: dict, type: KBSymbolicType, context: Context):
    print('Estimate string type')
    
def estimate_number_type(type_et: dict, type: KBNumericType, context: Context):
    print('Estimate number type')

def estimate_fuzzy_type(type_et: dict, type: KBFuzzyType, context: Context):
    print('Estimate fuzzy type')


def estimate_type(etalon_type: dict, type: KBType, context: Context):
    print('Estimate type')

    type_et = KBType.from_dict(etalon_type)
    if type.id == type_et.id:
        if type.meta == "string":
            if isinstance(type, KBSymbolicType):
                estimate_string_type(type_et, type, context=context.create_child('string type attr'))
        if type.meta == "number":
            if isinstance(type, KBNumericType):
                estimate_number_type(type_et, type, context=context.create_child('number type attr'))
        if type.meta == "fuzzy":
            if isinstance(type, KBFuzzyType):
                estimate_fuzzy_type(type_et, type, context=context.create_child('fuzzy type attr'))

def estimate_property():
    print('Estimate property')

def estimate_object(etalon_object: dict, object: KBClass, context: Context):
    print('Estimate object')
    
    object_et = KBClass.from_dict(etalon_object)
    for property in object_et.properties:
        estimate_property(property, object, context=context.create_child('properties').create_child(property.id))


def estimate_event(etalon_event: dict, event: KBEvent, context: Context):
    print('Estimate event')
    
    event_et = KBEvent.from_dict(etalon_event)
    if event_et.id == event.id:
        estimate_condition(event_et.occurance_condition, event.occurance_condition, context=context.create_child('open condition'))


def estimate_interval(etalon_interval: dict, interval: KBInterval, context: Context):
    print('Estimate interval')
    
    interval_et = KBInterval.from_dict(etalon_interval)
    if interval_et.id == interval.id:
        estimate_condition(interval_et.open, interval.open, context=context.create_child('open condition'))
        estimate_condition(interval_et.close, interval.close, context=context.create_child('close condition'))

def estimate_rule(etalon_rule: dict, rule: KBRule, context: Context):
    
    rule_et = KBRule.from_dict(etalon_rule)
    if rule_et.id == rule_et.id:
        estimate_rule_condition(rule_et.condition, rule.condition, context=context.create_child('condition'))
        estimate_instructions(rule_et.instructions, rule.instructions, context=context.create_child('instructions'))
        estimate_instructions(rule.else_instructions, context=context.create_child('else_instructions'))


from at_tutoring_skills.core import copmarison

from typing import List
from at_krl.core.kb_type import KBType, KBFuzzyType, KBNumericType, KBSymbolicType
from at_krl.core.kb_class import KBClass
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
# from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_rule import KBRule
from at_tutoring_skills.core.copmarison import Comparison, ComparisonResult
from at_tutoring_skills.core.errors import StudentMistakeException, Context, WrongNumberOfAttributes
from at_tutoring_skills.core.errors import OperandsTypesConflict, OperandsBaseTypesConflict, OperandNOperationConflict, InvalidCharacter, InvalidNumber, ELementNotFound

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

    # except Exception as e:
    #     array.append(e)
    # raise ExceptionGroup('errors', e)

def estimate_string_type(type: KBSymbolicType, type_et: KBSymbolicType, context: Context):
    print('Estimate string type')
    errors_list =[]

    check =type_et.values
    check_et = type_et.values

    if len(check) > len(check_et):
        errors_list.append(WrongNumberOfAttributes('Введено больше значений аттрибутов, чем требуется, в типе {type.id}'))
        return errors_list
    if len(check) < len(check_et):
        errors_list.append(WrongNumberOfAttributes('Введено меньше значений аттрибутов, чем требуется, в типе {type.id}'))
        return errors_list
    
    for j in range(len(check_et)):
        for i in range (len(check)):
            if check[i] == check_et[j]:
                check[j] = None
                check_et[j] = None
        if check_et[j]!= None:
            errors_list.append(InvalidCharacter('Введено неверное значение в типе {type.id}: {check[i]}'))
    
    return errors_list

#допустим готово
def estimate_number_type(type_et: KBNumericType, type: KBNumericType, context: Context):
    errors_list =[]
    print('Estimate number type')
    e = None
    if type._from.type != float and type._from.type != int:
        print('Внутренняя ошибка')

    
    result1 : ComparisonResult = Comparison.compare_numbers(type._from, type_et._from)
    result2 : ComparisonResult  = Comparison.compare_numbers(type._to, type_et._to)
    if result1.isEqual == True:
        print ('Значения ОТ {type.id} совпадают')
    else:
        errors_list.append(InvalidNumber('Введено неверное значение ОТ {type.id}'))

    if result2.isEqual == True:
        print ('Значения ДО {type.id} совпадают')
    else:
        errors_list.append(InvalidNumber('Введено неверное значение ДО {type.id}'))
        
    return errors_list

    
def estimate_fuzzy_type(type_et: KBFuzzyType, type: KBFuzzyType, context: Context):
    print('Estimate fuzzy type')

def estimate_type(etalon_type: KBType, type: KBType, context: Context):
    print('Estimate type')

    type_et = KBType.from_dict(etalon_type)
    if type.id == type_et.id:
        if type.meta == "string":
            if isinstance(type, KBSymbolicType):
                estimate_string_type( type,type_et, context=context.create_child('string type attr'))
        if type.meta == "number":
            if isinstance(type, KBNumericType):
                estimate_number_type(type, type_et, context=context.create_child('number type attr'))
        if type.meta == "fuzzy":
            if isinstance(type, KBFuzzyType):
                estimate_fuzzy_type(type, type_et, context=context.create_child('fuzzy type attr'))

    # exept ... as s:
    # handler_error()
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


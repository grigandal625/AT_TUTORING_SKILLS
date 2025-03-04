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
from at_tutoring_skills.core.errors import Typo, ForeginAttribute, OperandsTypesConflict, OperandsBaseTypesConflict, OperandNOperationConflict, InvalidCharacter, InvalidNumber, ELementNotFound

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


# все тексты ошибок заглушки, потом переписать

##################################### тип ####################################
def estimate_string_type(type: KBSymbolicType, type_et: KBSymbolicType, context: Context):
    print('Estimate string type')
    errors_list =[]

    check = type_et.values
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
        
        # raise ExceptionGroup('Ошибки, допущенные в атрибутах символьного типа {type.id}')
    # return 

def estimate_number(num1, num2, contex: Context):
    print(' ')
    if num1 != num2:
        return False
    else: return True
    
def estimate_number_type(type_et: KBNumericType, type: KBNumericType, context: Context):
    errors_list = []
    print('Estimate number type')

    if type(type._from) != int or type(type._from) != float: 
        errors_list.append(InvalidNumber('' , type._from) )
    if type(type._to)!= int or type(type._to)!= float:
        errors_list.append(InvalidNumber('' , type._to) )


    # Перевірка _from
    if not estimate_number(type._from, type_et._from, context):
        errors_list.append(InvalidNumber('' , type._from) )

    if not estimate_number(type._to, type_et._to, context):
        errors_list.append(InvalidNumber('' , type._to) )
                                                            
    # if errors_list:
    #     raise ExceptionGroup("Number type estimation errors", errors_list)

    return errors_list

def estimate_fuzzy_type(type_et: KBFuzzyType, type: KBFuzzyType, context: Context):
    print('Estimate fuzzy type')
    errors_list = []
    for mem_func_et in type_et.membership_functions():
        for mem_func in type.membership_functions():
            if mem_func_et.name == mem_func.name:
                # if mem_func_et.params!= mem_func.params:
                #     errors_list.append(OperandNOperationConflict('' , f'Несовпадение параметров для функции {mem_func_et.name}'))
                if mem_func_et.min == mem_func_et.min:
                    errors_list.append(InvalidNumber('' , f'Несовпадение минимальных значений для функции {mem_func_et.name}'))
                if mem_func_et.max == mem_func_et.max:
                    errors_list.append(InvalidNumber('' , f'Несовпадение максимальных значений для функции {mem_func_et.name}'))
                
                for point_et in mem_func_et.points:
                    flag = 0
                    for point in mem_func.points:
                        if point.x == point_et.x and point.y == point_et.y:
                            flag = 1
                    if flag == 1:
                        errors_list.append(InvalidNumber('', (point.x, point.y)))
            else:
                errors_list.append(ForeginAttribute('', f'Функции {mem_func_et.name} яавляется лишней'))

    return errors_list
    # points: List[MFPoint] | Iterable[MFPoint] = None
    # name: str = None
    # min: float = None
    # max: float = None

# class MFPoint(KBEntity):
#     x: float|int = None
#     y: float|int = None

def estimate_type(etalon_type: KBType, type: KBType, context: Context):
    print('Estimate type')
    errors_list = []
    type_et = KBType.from_dict(etalon_type)
    if type.id == type_et.id:
        if type.meta == "string":
            if isinstance(type, KBSymbolicType):
                errors_list = estimate_string_type( type,type_et, context=context.create_child('string type attr'))
        if type.meta == "number":
            if isinstance(type, KBNumericType):
                errors_list = estimate_number_type(type, type_et, context=context.create_child('number type attr'))
        if type.meta == "fuzzy":
            if isinstance(type, KBFuzzyType):
                errors_list = estimate_fuzzy_type(type, type_et, context=context.create_child('fuzzy type attr'))
    if errors_list:
        raise ExceptionGroup(...) # из всех эксепшнов в списке
    else:
        return ...
    # exept ... as s:
    # handler_error()

# def estimate_property():
#     print('Estimate property')

##################################### объект ####################################
def estimate_object(object_et: KBClass, object: KBClass, context: Context):
    print('Estimate object')
    errors_list = []

    for property_et in object_et.properties:
        flag = 0
        for property in object.properties:
            e = Comparison.levenshtein_distance(property.source, property_et.source)
            min_val = min(e, min_val)
            if e == 0:
                flag = 1
                break
            
        if flag == 0:
            if min_val == 1:
                errors_list.append(Typo('', f'Свойство {property_et.source} является лишним'))
            else:
                errors_list.append(InvalidCharacter('', f'Свойство {property_et.source} является несовпадающим'))
    if errors_list:
        raise ExceptionGroup('Ошибки при оценке объекта', errors_list)

# class KBProperty(KBInstance):
#     source: str = None

##################################### событие ####################################
def estimate_event(etalon_event: dict, event: KBEvent, context: Context):
    print('Estimate event')
    
    event_et = KBEvent.from_dict(etalon_event)
    if event_et.id == event.id:
        estimate_condition(event_et.occurance_condition, event.occurance_condition, context=context.create_child('open condition'))


##################################### интервал ####################################
def estimate_interval(etalon_interval: dict, interval: KBInterval, context: Context):
    print('Estimate interval')
    
    interval_et = KBInterval.from_dict(etalon_interval)
    if interval_et.id == interval.id:
        estimate_condition(interval_et.open, interval.open, context=context.create_child('open condition'))
        estimate_condition(interval_et.close, interval.close, context=context.create_child('close condition'))

##################################### правило ####################################
def estimate_rule(etalon_rule: dict, rule: KBRule, context: Context):
    
    rule_et = KBRule.from_dict(etalon_rule)
    if rule_et.id == rule_et.id:
        estimate_rule_condition(rule_et.condition, rule.condition, context=context.create_child('condition'))
        estimate_instructions(rule_et.instructions, rule.instructions, context=context.create_child('instructions'))
        estimate_instructions(rule.else_instructions, context=context.create_child('else_instructions'))

#осталось только estimate condotion

def estimate_condition() :
    print('Estimate condition')
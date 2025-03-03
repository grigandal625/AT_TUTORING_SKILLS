from dataclasses import dataclass, field
from typing import List


class Fine:
    SYNTAX_ERROR = 3
    LEXICAL_ERROR = 1
    LOGIC_ERROR = 2

class Coefficient:
    TYPE_COEFFICIENT = 0.75
    OBJECT_COEFFICIENT = 0.75
    EVENT_COEFFICIENT = 1
    INTERVAL_COEFFICIENT = 1
    RULE_COEFFICIENT = 1.25

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
    # fine: None
    def __init__(self, msg, context: Context, *args):
        super().__init__(msg, *args)
        self.context = context
        # self.fine = None

# далее описание всех ошибок

class SyntaxError(StudentMistakeException):
    fine = Fine.SYNTAX_ERROR
    def __init__(self, msg, context: Context, *args, fine):
        super().__init__(msg, *args)
        self.fine = fine

class LexicalError(StudentMistakeException):
    fine = Fine.LEXICAL_ERROR

class LogicError(StudentMistakeException):
    fine = Fine.LOGIC_ERROR

# далее подробно ошибки, можно разбить еще больше 
#################################### логика ################################

# конфлик типов с алленом
class OperandsTypesConflict(LogicError):
    # operand1 : None
    # operand2 : None
    # def __init__(self, msg, context: Context, operand1, operand2):
    #     super().__init__(msg, context, operand1, operand2)
        # self.operand1 = operand1
        # self.operand2 = operand2
        # self.context = context
    def __str__(self):
        return 'operands need to be of the same base type '
    
# конфлик базовых типов у операндов
class OperandsBaseTypesConflict(LogicError):
    
    # operand1 : None
    # operand2 : None
    def __str__(self):  
        return 'operands need to be of the same base type'
    
# неверное использование операндов в конкретной операции
class OperandNOperationConflict(LogicError):
    def __str__(self):
        return ''
class WrongNumberOfAttributes(LogicError):
    def __str__(self):
        return 'not enough attributes'
##################################### лексика ####################################

class InvalidCharacter(LexicalError):
    def __str__(self):
        return 'invalid character'
    
class InvalidNumber(LexicalError):
    def __str__(self):
        return 'invalid number'

##################################### cинтаксис ####################################
# не введен фрагмент
class ELementNotFound(SyntaxError):
    def __str__(self):
        return 'not found'
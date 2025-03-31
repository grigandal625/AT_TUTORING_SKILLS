class Fine:
    SYNTAX_ERROR = 3
    LOGIC_ERROR = 2
    LEXICAL_ERROR = 1


class Coefficient:
    TYPE_COEFFICIENT = 0.75
    OBJECT_COEFFICIENT = 0.75
    EVENT_COEFFICIENT = 1
    INTERVAL_COEFFICIENT = 1
    RULE_COEFFICIENT = 1.25


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
        return "operands need to be of the same base type "


# конфлик базовых типов у операндов
class OperandsBaseTypesConflict(LogicError):
    # operand1 : None
    # operand2 : None
    def __str__(self):
        return "operands need to be of the same base type"


# неверное использование операндов в конкретной операции
class OperandNOperationConflict(LogicError):
    def __str__(self):
        return ""


class WrongNumberOfAttributes(LogicError):
    def __str__(self):
        return "not enough attributes"


class ForeginAttribute(LogicError):
    def __str__(self):
        return "foreign attribute"


class InvalidNumberOfAttributes(LogicError):
    def __str__(self):
        return "invalid number of attributes"


##################################### лексика ####################################


class InvalidCharacter(LexicalError):
    def __str__(self):
        return "invalid character"


class InvalidNumber(LexicalError):
    def __str__(self):
        return "invalid number"


class Typo(LexicalError):
    def __str__(self):
        return "typo"

    fine = Fine.LEXICAL_ERROR / 2


##################################### cинтаксис ####################################
# не введен фрагмент
class ELementNotFound(SyntaxError):
    def __str__(self):
        return "not found"

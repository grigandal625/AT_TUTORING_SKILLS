from at_tutoring_skills.core.knowledge_base.rule.logic import KBRuleServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.rule.syntax import KBRuleServiceSyntax


class KBRuleService(KBRuleServiceSyntax, KBRuleServiceLogicLexic):
    """Сервис для работы с правилами в базе знаний.
    
    Наследует функциональность:
    - KBRuleServiceSyntax: обработка синтаксических ошибок в правилах
    - KBRuleServiceLogicLexic: логическая обработка и анализ правил
    """
    pass
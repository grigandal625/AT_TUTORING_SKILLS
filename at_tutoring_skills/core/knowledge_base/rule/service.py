from at_tutoring_skills.core.knowledge_base.rule.logic import KBRuleServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.type.syntax import KBTypeServiceSyntax
from at_tutoring_skills.core.task.service import Repository


class KBRuleService(KBTypeServiceSyntax, KBRuleServiceLogicLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

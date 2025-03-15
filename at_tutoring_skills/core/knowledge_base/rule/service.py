from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.rule.logic import KBRuleServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.type.syntax import KBTypeServiceSyntax


class KBRuleService(KBTypeServiceSyntax, KBRuleServiceLogicLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

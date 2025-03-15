from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.type.logic import KBTypeServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.type.syntax import KBTypeServiceSyntax


class KBTypeService(KBTypeServiceSyntax, KBTypeServiceLogicLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

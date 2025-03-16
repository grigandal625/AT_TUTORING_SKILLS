from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.event.syntax import KBObjectServiceSyntax
from at_tutoring_skills.core.knowledge_base.object.logic import KBObjectServiceLogicLexic


class KBEventService(KBObjectServiceSyntax, KBObjectServiceLogicLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

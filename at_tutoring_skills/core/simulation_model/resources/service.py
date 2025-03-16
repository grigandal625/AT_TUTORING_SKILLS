from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.event.syntax import IMObjectServiceSyntax
from at_tutoring_skills.core.knowledge_base.object.logic import IMObjectServiceLogicLexic


class IMEventService(IMObjectServiceSyntax, IMObjectServiceLogicLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

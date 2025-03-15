from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.interval.logic import KBIntervalServiceLogixLexic
from at_tutoring_skills.core.knowledge_base.interval.syntax import KBIntervalServiceSyntax


class KBIntervalService(KBIntervalServiceSyntax, KBIntervalServiceLogixLexic):
    def __init__(self, repository: Repository):
        self.repository = repository

from at_tutoring_skills.core.knowledge_base.event.logic import KBEventServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.event.syntax import KBEventServiceSyntax

# from at_tutoring_skills.core.task.service import Repository


class KBEventService(KBEventServiceSyntax, KBEventServiceLogicLexic):
    ...


#     def __init__(self, repository: Repository):
#         self.repository = repository

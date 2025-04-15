from at_tutoring_skills.core.knowledge_base.object.logic import KBObjectServiceLogicLexic
from at_tutoring_skills.core.knowledge_base.object.syntax import KBObjectServiceSyntax

# if TYPE_CHECKING:
#     from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService


class KBObjectService(KBObjectServiceSyntax, KBObjectServiceLogicLexic):
    pass

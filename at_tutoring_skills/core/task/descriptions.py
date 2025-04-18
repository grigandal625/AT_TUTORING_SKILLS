from at_tutoring_skills.apps.skills.models import Task

from at_krl.models.kb_type import KBNumericTypeModel, KBSymbolicTypeModel, KBFuzzyTypeModel
from at_krl.models.kb_entity import KBRootModel


class KBTypeRootModel(KBRootModel[KBNumericTypeModel | KBSymbolicTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context)

class DescriptionsService:

    async def get_task_entity(self, task):
        pass
from at_krl.models.kb_class import KBClassModel
from at_krl.models.kb_entity import KBRootModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.models.kb_type import KBFuzzyTypeModel
from at_krl.models.kb_type import KBNumericTypeModel
from at_krl.models.kb_type import KBSymbolicTypeModel
from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.utils.context import Context
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.apps.skills.models import User

env = Environment(loader=PackageLoader("at_tutoring_skills.core.task"), autoescape=select_autoescape())


class KBTypeRootModel(KBRootModel[KBNumericTypeModel | KBSymbolicTypeModel | KBFuzzyTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context)


class DescriptionsService:
    KB_SUBJECT_TO_MODEL = {
        SUBJECT_CHOICES.KB_TYPE: KBTypeRootModel,
        SUBJECT_CHOICES.KB_OBJECT: KBClassModel,
        SUBJECT_CHOICES.KB_RULE: KBRuleModel,
        SUBJECT_CHOICES.KB_EVENT: KBEventModel,
        SUBJECT_CHOICES.KB_INTERVAL: KBIntervalModel,
    }

    async def get_kb_task_description(self, task: Task, user: User, short=False):
        task_user = await TaskUser.objects.filter(task=task, user=user).select_related("task", "user").afirst()
        return env.get_template("descriptions/task_description.md.jinja2").render(
            task=task, task_user=task_user, service=self, short=short
        )

    def get_kb_task_entity(self, task: Task):
        ctx = Context(name="generate_description")
        model = self.KB_SUBJECT_TO_MODEL[task.task_object](**task.object_reference)
        return model.to_internal(context=ctx)

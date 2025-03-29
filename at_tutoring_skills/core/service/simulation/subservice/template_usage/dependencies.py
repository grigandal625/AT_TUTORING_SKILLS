from typing import Protocol

from pydantic import BaseModel

from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import (
    TemplateMetaResponse,
)
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import (
    ResourceTypesResponse,
)

class IMistakeService(Protocol):
    def create_mistake(self, mistake: CommonMistake, user_id: int) -> int: ...


class ITaskService(Protocol):
    def get_object_reference(self, object_name: str, object_class) -> BaseModel: ...


class IResourceComponent(Protocol):
    def get_resource(self, id: int) -> TemplateMetaResponse: ...


class ITemplateComponent(Protocol):
    def get_template(self, id: int) -> ResourceTypesResponse: ...
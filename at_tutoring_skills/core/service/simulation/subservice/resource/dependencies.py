from typing import Protocol

from pydantic import BaseModel

from at_tutoring_skills.core.errors.models import CommonMistake


class IMistakeService(Protocol):
    def create_mistake(self, mistake: CommonMistake, user_id: int) -> int: ...


class ITaskService(Protocol):
    def get_object_reference(self, object_name: str, object_class) -> BaseModel: ...

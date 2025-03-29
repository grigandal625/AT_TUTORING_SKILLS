from typing import Protocol

from pydantic import BaseModel

from at_tutoring_skills.core.errors.models import CommonMistake


class IMistakeService(Protocol):
    def create_mistake(self, user_id: int, event: str, object_name: str): ...
        # try:
        #     self.repository.create_mistake(mistake, user_id)
        # except Exception as e:
        #     raise ValueError(f"Failed to create mistake: {e}") from e

class ITaskService:
    def __init__(self, repository: IMistakeService):
        self.repository = repository

    def complete_task(self, user_id: int, event: str, object_name: str):
        self.repository.create_mistake(user_id, event, object_name)

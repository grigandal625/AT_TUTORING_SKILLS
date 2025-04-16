from typing import Protocol



class IMistakeService(Protocol):
    def create_mistake(self, user_id: int, event: str, object_name: str):
        ...

    # try:
    #     self.repository.create_mistake(mistake, user_id)
    # except Exception as e:
    #     raise ValueError(f"Failed to create mistake: {e}") from e


class ITaskService(Protocol):
    def __init__(self, repository: IMistakeService):
        self.repository = repository

    def complete_task(self, user_id: int, event: str, object_name: str):
        self.repository.create_mistake(user_id, event, object_name)


class MistakeService:
    def create_mistake(self, user_id: int, event: str, object_name: str) -> int:
        print(f"Creating mistake for user {user_id}, event '{event}', object '{object_name}'")
        return 1


class TaskService:
    def __init__(self, mistake_service: MistakeService):
        self.mistake_service = mistake_service

    def complete_task(self, user_id: int, event: str, object_name: str):
        print(f"Completing task for user {user_id}, event '{event}', object '{object_name}'")
        self.mistake_service.create_mistake(user_id, event, object_name)

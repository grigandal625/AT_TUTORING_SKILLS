from typing import Protocol


class Repository(Protocol):
    # Логика добавления ошибка в БД из Django
    def complete_task(self, user_id: int, event: str, object_name: str): ...
    # Добавить запись в таблицу TaskUser


class TaskService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def complete_task(self, user_id: int, event: str, object_name: str):
        self.repository.complete_task(user_id, event, object_name)

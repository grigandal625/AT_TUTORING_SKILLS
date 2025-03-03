from typing import Protocol


class Repository(Protocol):
    # Логика добавления ошибка в БД из Django
    def create_mistake(self, mistake: CommonMistake): ...


class KBTypeService:
    def __init__(self, repository: Repository):
        self.repository = repository

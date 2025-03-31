from typing import Protocol

from pydantic import BaseModel
from at_krl.utils.context import Context as ATKRLContext

from at_tutoring_skills.core.errors.models import CommonMistake


class IMistakeService(Protocol):
    def create_mistake(self, mistake: CommonMistake, user_id: int) -> int:
        ...

class ITaskService:
    async def get_object_reference(self, object_name: str, object_class): ...

# class ITaskService(Protocol):
#     async def get_object_reference(self, object_name: str, object_class) -> BaseModel: ...
        
        
        
#         d = task.object_reference #jsom
#         kb_type = KBTypeRootModel(**d)
#         return kb_type.to_internal(context)

# from asgiref.sync import sync_to_async
# import logging
# from django.db import transaction
# from pydantic import RootModel

# from at_tutoring_skills.core.models.resource_types import (
#     ResourceTypeRequest, 
#     ResourceTypeResponse
# )
# from at_tutoring_skills.core.context import ATKRLContext
# from at_tutoring_skills.core.errors.models import CommonMistake

# logger = logging.getLogger(__name__)

# class ResourceTypeRootModel(RootModel[ResourceTypeRequest | ResourceTypeResponse]):
#     """Pydantic RootModel для валидации типов ресурсов"""
    
#     def to_internal(self, context: ATKRLContext):
#         """Конвертация в внутреннее представление системы"""
#         return self.root.to_internal(context=context)

# class ResourceTypeService:
#     async def get_type_reference(self, task: Task) -> ResourceTypeRootModel:
#         """
#         Асинхронно получает ссылку на тип ресурса из задачи
#         """
#         try:
#             # Создаем контекст выполнения
#             context = ATKRLContext(name="resource_type_validation")
            
#             # Получаем сырые данные из задачи
#             raw_data = task.object_reference
            
#             # Валидируем данные через Pydantic модель
#             validated_type = ResourceTypeRootModel(**raw_data)
            
#             # Конвертируем во внутренний формат системы
#             return await sync_to_async(validated_type.to_internal)(context)
            
#         except ValidationError as e:
#             logger.error(f"Resource type validation error: {str(e)}")
#             raise ValueError("Invalid resource type data structure") from e
#         except Exception as ex:
#             logger.exception("Unexpected error in resource type processing")
#             raise RuntimeError("Resource type processing failed") from ex
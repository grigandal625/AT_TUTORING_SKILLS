import json
from asyncio.log import logger
import json
from jsonschema import ValidationError
from pydantic import BaseModel
from datetime import datetime
import datetime
from operator import index
from typing import Dict, List, Optional

from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import authorized_method
from jsonschema import ValidationError
from pydantic import BaseModel

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.service.simulation.subservice.function.service import FunctionService
from at_tutoring_skills.core.service.simulation.subservice.resource.models.models import ResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.resource.service import ResourceService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.models.models import ResourceTypeRequest
from at_tutoring_skills.core.service.simulation.subservice.resource_type.service import ResourceTypeService
from at_tutoring_skills.core.service.simulation.subservice.template.models.models import RelevantResourceRequest
from at_tutoring_skills.core.service.simulation.subservice.template.service import TemplateService
from at_tutoring_skills.core.service.simulation.subservice.template_usage.models.models import TemplateUsageArgumentRequest
from at_tutoring_skills.core.service.simulation.subservice.template_usage.service import TemplateUsageService
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.task.transitions import TransitionsService


class SimulationService(ATComponent):
    main_task_service = None
    main_task_cache = None
    cash: dict = None

    def __init__(
        self,
        connection_parameters,
        resource_type_service: ResourceTypeService,
        resource_service: ResourceService,
        template_service: TemplateService,
        template_usage_service: TemplateUsageService,
        function_service: FunctionService,
    ):
        super().__init__(connection_parameters=connection_parameters)
        self.resource_type_service = resource_type_service
        self.resource_service = resource_service
        self.template_service = template_service
        self.template_usage_service = template_usage_service
        self.function_service = function_service
        self.main_task_service = TaskService()
        self.transition_service = TransitionsService()
        self.cash = {}

    async def get_user_id_or_token(self, auth_token: str) -> int | str:
        if await self.check_external_registered("AuthWorker"):
            user_id = await self.exec_external_method(
                reciever="AuthWorker",
                methode_name="verify_token",
                method_args={"token": auth_token},
            )
            return user_id
        return auth_token

    async def create_user(self, auth_token: str) -> tuple[User, bool]:
        try:
            user, created = await User.objects.aget_or_create(
                user_id=auth_token,
            )

            if created:
                logger.info(f"Created new user: {auth_token}")
            else:
                logger.debug(f"User already exists: {auth_token}")

            return user, created

        except Exception as e:
            logger.error(f"Error creating user {auth_token}: {str(e)}")
            raise

    # временное решение для обработки
    def init_cash(self, auth_token: str):
        if auth_token not in self.cash:
            self.cash[auth_token] = {"im_resourceTypes": [], "im_resources": [], "im_templates": []}

    # ============================================ Cash Resource Types =====================================================
    def add_im_resource_type_to_cash(self, resource_type: BaseModel, auth_token: int):
        # Получение уникального идентификатора из модели
        resource_type_id = getattr(resource_type, "id", None)

        if not resource_type_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")

        # Сохранение данных в кэш
        self.cash[resource_type_id] = {
            "data": resource_type.dict(),  # Преобразуем Pydantic модель в словарь для хранения
            "auth_token": auth_token,
        }

    def get_im_resource_type_from_cash(self, resource_type_id: int):
        cached_data = self.cash.get(resource_type_id)

        if cached_data:
            print(f"Запись с ID {resource_type_id} найдена в кэше.")
            return cached_data["data"]
        else:
            print(f"Запись с ID {resource_type_id} не найдена в кэше.")
            return None

    def get_resource_type_names_from_cache(self, rel_resources: List[RelevantResourceRequest]) -> List[Dict[str, str]]:
        resource_data = []

        for resource in rel_resources:
            if resource.resource_type_id is not None:
                cached_data = self.get_im_resource_type_from_cash(resource.resource_type_id)

                if cached_data:
                    try:
                        if isinstance(cached_data, str):
                            # Если resource_type — строка, пытаемся разобрать её как JSON
                            resource_type_data = json.loads(cached_data)
                        elif isinstance(cached_data, dict):
                            # Если resource_type уже словарь, используем его напрямую
                            resource_type_data = cached_data
                        else:
                            raise ValueError("Некорректный тип данных для resource_type. Ожидалась строка или словарь.")

                        # Создаем объект ResourceTypeRequest
                        resource_type_obj = ResourceTypeRequest(**resource_type_data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        print(f"Ошибка при преобразовании resource_type: {e}")
                        return

                    resource_data.append({"resource_type_str": resource_type_obj.name, "name": resource.name})
                else:
                    print(f"Resource с ID {resource.resource_type_id_str} не найден в кэше.")
            else:
                print(f"Resource ID отсутствует для ресурса с именем {resource.name}.")

        return resource_data

    # ============================================ Cash Resource =====================================================
    def add_im_resource_to_cash(self, resource: BaseModel, auth_token: int):
        # Получение уникального идентификатора из модели
        resource_id = getattr(resource, "id", None)

        if not resource_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")

        # Сохранение данных в кэш
        self.cash[resource_id] = {
            "data": resource.dict(),  # Преобразуем Pydantic модель в словарь для хранения
            "auth_token": auth_token,
        }

    def get_im_resource_from_cash(self, resource_id: int):
        cached_data = self.cash.get(resource_id)
        
        if cached_data:
            print(f"Запись с ID {resource_id} найдена в кэше.")
            return cached_data['data']
        else:
            print(f"Запись с ID {resource_id} не найдена в кэше.")
            return None


    def get_resource_names_from_cache(self, arguments: List[TemplateUsageArgumentRequest]) -> List[dict]:
        """
        Получает имена ресурсов из кэша и возвращает их вместе с типами.
        """
        resource_data = []

        for argument in arguments:
            if argument.resource_id is not None:
                # Получаем данные из кэша
                cached_data = self.get_im_resource_from_cash(argument.resource_id)

                if cached_data:
                    try:
                        # Преобразуем cached_data в словарь
                        if isinstance(cached_data, str):
                            # Если cached_data — строка, пытаемся разобрать её как JSON
                            resources_data = json.loads(cached_data)
                        elif isinstance(cached_data, dict):
                            # Если cached_data уже словарь, используем его напрямую
                            resources_data = cached_data
                        else:
                            raise ValueError("Некорректный тип данных для cached_data. Ожидалась строка или словарь.")

                        # Создаем объект ResourceTypeRequest
                        resource_type_obj = ResourceRequest(**resources_data)

                        # Добавляем данные в результат
                        resource_data.append({
                            "name": resource_type_obj.name,
                        })

                    except (json.JSONDecodeError, ValidationError) as e:
                        print(f"Ошибка при преобразовании cached_data для resource ID {argument.resource_id}: {e}")
                        continue  # Пропускаем текущий элемент и продолжаем обработку

                else:
                    print(f"Resource с ID {argument.resource_id} не найден в кэше.")
            else:
                print(f"Resource ID отсутствует для ресурса с именем {argument.resource_id_str}.")

        return resource_data

# ============================================ Cash Template =====================================================
    def add_im_template_to_cash(self, template: BaseModel, auth_token: int):
        # Получение уникального идентификатора из модели
        template_id = getattr(template, "id", None)
        
        if not template_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")
        
        # Сохранение данных в кэш
        self.cash[template_id] = {
            "data": template.dict(),  # Преобразуем Pydantic модель в словарь для хранения
            "auth_token": auth_token
        }

    def get_im_template_from_cash(self, template_id: int):
        cached_data = self.cash.get(template_id)

        if cached_data:
            print(f"Запись с ID {template_id} найдена в кэше.")
            return cached_data['data']
        else:
            print(f"Запись с ID {template_id} не найдена в кэше.")
            return None

    def get_template_name_from_cache(self, template_id: int) -> Optional[str]:

        cached_data = self.get_im_template_from_cash(template_id)

        if not cached_data:
            return None

        try:
            if isinstance(cached_data, str):
                resources_data = json.loads(cached_data)
                
            elif isinstance(cached_data, dict):
                resources_data = cached_data
            else:
                raise ValueError("Некорректный тип данных для cached_data. Ожидалась строка или словарь.")

            # Извлекаем имя шаблона
            template_name = resources_data.get("name")
            if template_name is None:
                raise KeyError("Поле 'name' отсутствует в данных шаблона.")

            return template_name

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Ошибка при обработке данных шаблона с ID {template_id}: {e}")
            return None

    #   ============================= Resource Types ====================================
    @authorized_method
    async def handle_resource_type(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал тип ресурса (ИМ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)

        await self.main_task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Syntax Mistakes: {e}") from e

        task: Task = await self.main_task_service.get_task_by_name(
            resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES
        )

        if not task:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

        else:
            self.add_im_resource_type_to_cash(resource_type, auth_token)

            print(task.object_name, task.object_reference, resource_type)

            errors_list = []
            errors_list_logic = await self.resource_type_service.handle_logic_mistakes(user_id, resource_type)
            errors_list_lexic = await self.resource_type_service.handle_lexic_mistakes(user_id, resource_type)

            if errors_list_logic:
                errors_list.extend(errors_list_logic)
            if errors_list_lexic:
                errors_list.extend(errors_list_lexic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.main_task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 6)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}

            else:  # Преобразуем объекты CommonMistake в словари
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                return {"status": "error", "message": f"Обнаружены ошибки: {errors_message}", "stage_done": False}

    #   ==============================    Resource   ====================================
    @authorized_method
    async def handle_resource(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал ресурс (ИМ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)

        await self.main_task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            resource = await self.resource_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Syntax Mistakes: {e}") from e

        task: Task = await self.main_task_service.get_task_by_name(resource.name, SUBJECT_CHOICES.SIMULATION_RESOURCES)

        if not task:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

        else:
            self.add_im_resource_to_cash(resource, auth_token)

            print(task.object_name, task.object_reference, resource)

            resource_type_name = self.get_im_resource_type_from_cash(resource.resource_type_id)

            errors_list = []
            errors_list_logic = await self.resource_service.handle_logic_mistakes(user_id, resource, resource_type_name)
            if errors_list_logic:
                errors_list.extend(errors_list_logic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.main_task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 7)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}

            else:  # Преобразуем объекты CommonMistake в словари
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                return {"status": "error", "message": f"Обнаружены ошибки: {errors_message}", "stage_done": False}

    #   =============================    Template   ================================
    @authorized_method
    async def handle_template(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал образец операции (ИМ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)

        await self.main_task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            template = await self.template_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Syntax Mistakes: {e}") from e

        task: Task = await self.main_task_service.get_task_by_name(
            template.meta.name, SUBJECT_CHOICES.SIMULATION_TEMPLATES
        )

        if not task:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

        else:
            self.add_im_template_to_cash(template.meta, auth_token)

            print(task.object_name, task.object_reference, template)

            resource_type_name = self.get_resource_type_names_from_cache(template.meta.rel_resources)

            errors_list = []
            errors_list_logic = await self.template_service.handle_logic_mistakes(user_id, template, resource_type_name)
            errors_list_lexic = await self.template_service.handle_lexic_mistakes(user_id, template, resource_type_name)

            if errors_list_logic:
                errors_list.extend(errors_list_logic)
            if errors_list_lexic:
                errors_list.extend(errors_list_lexic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.main_task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 8)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}

            else:  # Преобразуем объекты CommonMistake в словари
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                return {"status": "error", "message": f"Обнаружены ошибки: {errors_message}", "stage_done": False}

    #   ============================= Template Usage ================================
    @authorized_method
    async def handle_template_usage(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал операцию (ИМ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)

        await self.main_task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            template_usage = await self.template_usage_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Syntax Mistakes: {e}") from e

        task: Task = await self.main_task_service.get_task_by_name(
            template_usage.name, SUBJECT_CHOICES.SIMULATION_TEMPLATE_USAGES
        )

        if not task:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}
        
        else:
            print(task.object_name, task.object_reference, template_usage)

            resource_type_name = self.get_resource_names_from_cache(template_usage.arguments)
            template_name = self.get_template_name_from_cache(template_usage.template_id)

            errors_list = []
            errors_list_logic = await self.template_usage_service.handle_logic_mistakes(user_id, template_usage,  resource_type_name,  template_name)
            if errors_list_logic:
                errors_list.extend(errors_list_logic) 
                
            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.main_task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 9)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
            
            else: # Преобразуем объекты CommonMistake в словари
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                return {"status": "error", "message": f"Обнаружены ошибки: {errors_message}", "stage_done": False}


    #   =============================== Function =====================================
    @authorized_method
    async def handle_function(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал функцию (ИМ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)

        await self.main_task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            function = await self.function_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Syntax Mistakes: {e}") from e

        task: Task = await self.main_task_service.get_task_by_name(function.name, SUBJECT_CHOICES.SIMULATION_FUNCS)

        if not task:
            skill_result = "Задание не найдено, продолжайте выполнение работы"
            return skill_result
        else:
            print(task.object_name, task.object_reference, function)
            # await self.task_service.create_task_user_safe(task, user)

            errors_list = []
            errors_list_logic = await self.function_service.handle_logic_mistakes(user_id, function)
            errors_list_lexic = await self.function_service.handle_lexic_mistakes(user_id, function)

            if errors_list_logic:
                errors_list.extend(errors_list_logic)
            if errors_list_lexic:
                errors_list.extend(errors_list_lexic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.main_task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 7)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
            
            else: # Преобразуем объекты CommonMistake в словари
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                return {"status": "error", "message": f"Обнаружены ошибки: {errors_message}", "stage_done": False}


        # user_id = await self.get_user_id_or_token(auth_token)
        # user, created = await self.main_task_service.create_user(user_id)
        # await self.main_task_service.create_user_skill_connection(user)
        # user_id = user.pk
        # # self.main_task_service.create_task_user_safe(task, user)

        # try:
        #     resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)
        # except BaseException as e:
        #     raise ValueError(f"Handle IM Resource Type Created: Syntax Mistakes: {e}") from e

        # task : Task = await self.main_task_service.get_task_by_name(resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES)
        # print(task.object_name, task.object_reference)

        # if task:
        #     try:
        #         await self.resource_type_service.handle_logic_mistakes(user_id, resource_type)
        #     except BaseException as e:
        #         raise ValueError(f"Handle IM Resource Type Created: Logic Mistakes: {e}") from e

        #     try:
        #         await self.resource_type_service.handle_lexic_mistakes(user_id, resource_type)
        #     except BaseException as e:
        #         raise ValueError(f"Handle IM Resource Type Created: Lexic Mistakes: {e}") from e
        #     try:
        #         await self.main_task_service.complete_task(task, user)
        #     except BaseException as e:
        #         raise ValueError(f"Handle IM Resource Type Created: Complete Task: {e}") from e
        # else:
        #     return "Задание не найдено"


#         # ============================================ Cash  =====================================================
#     # Добавление объекта в кэш
#     def add_to_cash(self, array_name: str, data: dict, auth_token: str):
#         self.init_cash(auth_token)
#         if array_name not in self.cash[auth_token]:
#             raise ValueError(f"Array '{array_name}' does not exist in the cash.")

#         self.cash[auth_token][array_name].append(data)

#     # Тип ресурса
#     def add_im_resourceType_to_cash(self, data: dict, auth_token: str):
#         self.add_to_cash('im_resourceTypes', data, auth_token)


# # ============================== get from dict ==============================
#     @staticmethod
#     def im_resourceTypes_from_dict(resourcetype, event: str) -> dict:
#         new_resourcetype = {}
#         if resourcetype:
#             # Проверяем тип данных
#             if isinstance(resourcetype, dict):
#                 resourcetype_id = resourcetype.get('id')
#                 resourcetype_type = resourcetype.get('type')
#                 attributes = resourcetype.get('attributes', [])
#             else:
#                 # Если это Pydantic модель
#                 resourcetype_id = getattr(resourcetype, 'id', None)
#                 resourcetype_type = getattr(resourcetype, 'type', None)
#                 attributes = getattr(resourcetype, 'attributes', [])

#             # Заполняем новый словарь
#             new_resourcetype['typeId'] = resourcetype_id
#             new_resourcetype['meta'] = {1: 'constant', 2: 'temporal'}.get(resourcetype_type, 0)
#             new_resourcetype['attributes_processed'] = []

#             # Обработка атрибутов
#             for attr in attributes:
#                 processed_attr = {
#                     'attributeId': getattr(attr, 'id', None) if hasattr(attr, 'id') else attr.get('id'),
#                     'name': getattr(attr, 'name', None) if hasattr(attr, 'name') else attr.get('name'),
#                     'type': getattr(attr, 'type', None) if hasattr(attr, 'type') else attr.get('type'),
#                     'default': getattr(attr, 'default_value', None) if hasattr(attr, 'default_value') else attr.get('default_value')
#                 }
#                 # Обработка enum-атрибутов
#                 if processed_attr['type'] == 4:
#                     processed_attr['enum_values'] = getattr(attr, 'enum_values_set', []) if hasattr(attr, 'enum_values_set') else attr.get('enum_values_set', [])

#                 new_resourcetype['attributes_processed'].append(processed_attr)
#         else:
#             print("Ошибка: resourcetype пуст")
#         return new_resourcetype

#     # Обработка списка типов ресурсо
#     @authorized_method
#     async def handle_im_resource_types_get(self, event: str, data: dict, auth_token: str):
#         print('Извлечение списка типов ресурсов ', data)
#         resourceTypes_array = data['result']['items']
#         print(resourceTypes_array)
#         for item in resourceTypes_array:
#             resourceTypes_dict = self.im_resourceTypes_from_dict(item, event)
#             self.add_im_resourceType_to_cash(resourceTypes_dict, auth_token)


# # =================================== get value from element by key ===========================
#     # Универсальный метод для поиска значений по ключам
#     def get_smth_val_by_key(self, array_name: str, search_key: str, dest_key: str, key_value: str, auth_token: str):
#         self.init_cash(auth_token)
#         if array_name not in self.cash[auth_token]:
#             raise ValueError(f"Array '{array_name}' does not exist in the cash.")

#         array = self.cash[auth_token][array_name]

#         # Поиск элемента по ключу и значению
#         for item in array:
#             if item.get(search_key) == key_value:
#                 return item.get(dest_key)

#         raise KeyError(f"Element with {search_key}='{key_value}' not found in array '{array_name}'.")

#   =============================    Template   ================================
# def handle_template(self, event: str, data: dict, auth_token: int):
#     print("Обучаемый отредактировал образец операции (ИМ): ", data)
#     user_id = self.get_user_id_or_token(auth_token)
#     try:
#         template = TemplateService.handle_syntax_mistakes(user_id, data)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Created: Syntax Mistakes: {e}") from e

#     try:
#         TemplateService.handle_logic_mistakes(user_id, template)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Created: Logic Mistakes: {e}") from e

#     try:
#         TemplateService.handle_lexic_mistakes(user_id, template)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Created: Lexic Mistakes: {e}") from e

#     try:
#         ITaskService.complete_task(user_id, event, template.id)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Created: Complete Task: {e}") from e

# #   ============================= Template Usage ================================
# def handle_template_usage(self, event: str, data: dict, auth_token: int):
#     print("Обучаемый отредактировал тип ресурса (ИМ): ", data)
#     user_id = self.get_user_id_or_token(self, auth_token)
#     try:
#         template_usage = TemplateUsageService.handle_syntax_mistakes(user_id, data)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Usage Created: Syntax Mistakes: {e}") from e

#     try:
#         TemplateUsageService.handle_logic_mistakes(user_id, template_usage)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Usage Created: Logic Mistakes: {e}") from e

#     try:
#         TemplateUsageService.handle_lexic_mistakes(user_id, template_usage)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Usage Created: Lexic Mistakes: {e}") from e

#     try:
#         ITaskService.complete_task(user_id, event, template_usage.id)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Template Usage Created: Complete Task: {e}") from e

# #   ============================= Function =====================================
# @authorized_method
# async def handle_function(self, event: str, data: dict, auth_token: int):
#     print("Обучаемый отредактировал функцию (ИМ): ", data)
#     user_id = await self.get_user_id_or_token(auth_token)
#     user, created = await self.create_user(user_id)

#     try:
#         function = await self.function_service.handle_syntax_mistakes(user_id, data)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Function Created: Syntax Mistakes: {e}") from e

#     try:
#         await self.function_service.handle_logic_mistakes(user_id, function)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Function Created: Logic Mistakes: {e}") from e

#     try:
#         await self.function_service.handle_lexic_mistakes(user_id, function)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Function Created: Lexic Mistakes: {e}") from e

#     try:
#         ITaskService.complete_task(user_id, event, function.id)
#     except BaseException as e:
#         raise ValueError(f"Handle IM Function Created: Complete Task: {e}") from e

import json
from asyncio.log import logger
from typing import Dict
from typing import List
from typing import Optional

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
from at_tutoring_skills.core.service.simulation.subservice.template_usage.models.models import (
    TemplateUsageArgumentRequest,
)
from at_tutoring_skills.core.service.simulation.subservice.template_usage.service import TemplateUsageService
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.task.skill_service import SkillService
from at_tutoring_skills.core.task.transitions import TransitionsService


class SimulationService(ATComponent):
    task_service = None
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
        self.task_service = TaskService()
        self.transition_service = TransitionsService()
        self.skill_service = SkillService()
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
            self.cash[auth_token] = {
                "resource_types": {},  # Словарь для типов ресурсов
                "resources": {},  # Словарь для ресурсов
                "templates": {},  # Словарь для шаблонов
            }

    # ============================================ Cash Resource Types =====================================================
    def add_im_resource_type_to_cash(self, resource_type: BaseModel, auth_token: int):
        self.init_cash(auth_token)
        resource_type_id = getattr(resource_type, "id", None)

        if not resource_type_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")

        self.cash[auth_token]["resource_types"][resource_type_id] = {
            "data": resource_type.dict(),
            "auth_token": auth_token,
        }

    def get_im_resource_type_from_cash(self, resource_type_id: int, auth_token: int):
        self.init_cash(auth_token)
        cached_data = self.cash[auth_token]["resource_types"].get(resource_type_id)
        if cached_data:
            print(f"Запись типа ресурса с ID {resource_type_id} найдена в кэше.")
            return cached_data["data"]
        else:
            print(f"Запись типа ресурса с ID {resource_type_id} не найдена в кэше.")
            return None

    def get_resource_type_names_from_cache(
        self, rel_resources: List[RelevantResourceRequest], auth_token: int
    ) -> List[Dict[str, str]]:
        resource_data = []

        for resource in rel_resources:
            if resource.resource_type_id is not None:
                cached_data = self.get_im_resource_type_from_cash(resource.resource_type_id, auth_token)

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
        self.init_cash(auth_token)
        resource_id = getattr(resource, "id", None)

        if not resource_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")

        self.cash[auth_token]["resources"][resource_id] = {
            "data": resource.dict(),
            "auth_token": auth_token,
        }

    def get_im_resource_from_cash(self, resource_id: int, auth_token: int):
        self.init_cash(auth_token)
        cached_data = self.cash[auth_token]["resources"].get(resource_id)
        if cached_data:
            print(f"Запись ресурса с ID {resource_id} найдена в кэше.")
            return cached_data["data"]
        else:
            print(f"Запись ресурса с ID {resource_id} не найдена в кэше.")
            return None

    async def get_errors_result(self, errors_list, user, task, task_object):
        serialized_errors = [error.model_dump() for error in errors_list]
        errors_message = " ".join(
            [f"Ошибка №{i+1}: {error.get('tip', 'Неизвестная ошибка')}" for i, error in enumerate(serialized_errors)]
        )

        skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

        tasks = await self.task_service.get_variant_tasks_description(
            user, skip_completed=False, task_object=task_object
        )

        return {
            "status": "error",
            "message": f"Обнаружены ошибки: {errors_message}",
            "stage_done": False,
            "url": errors_message,
            "hint": tasks,
            "skills": skills,
        }

    def get_resource_names_from_cache(
        self, arguments: List[TemplateUsageArgumentRequest], auth_token: int
    ) -> List[dict]:
        """
        Получает имена ресурсов из кэша и возвращает их вместе с типами.
        """
        resource_data = []

        for argument in arguments:
            if argument.resource_id is not None:
                # Получаем данные из кэша
                cached_data = self.get_im_resource_from_cash(argument.resource_id, auth_token)

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
                        resource_data.append(
                            {
                                "name": resource_type_obj.name,
                            }
                        )

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
        self.init_cash(auth_token)
        template_id = getattr(template, "id", None)

        if not template_id:
            raise ValueError("Поле 'id' отсутствует в данных. Невозможно добавить в кэш.")

        self.cash[auth_token]["templates"][template_id] = {
            "data": template.dict(),
            "auth_token": auth_token,
        }

    def get_im_template_from_cash(self, template_id: int, auth_token: int):
        self.init_cash(auth_token)
        cached_data = self.cash[auth_token]["templates"].get(template_id)
        if cached_data:
            print(f"Запись шаблона с ID {template_id} найдена в кэше.")
            return cached_data["data"]
        else:
            print(f"Запись шаблона с ID {template_id} не найдена в кэше.")
            return None

    def get_template_name_from_cache(self, template_id: int, auth_token: int) -> Optional[str]:
        cached_data = self.get_im_template_from_cash(template_id, auth_token)

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

    #   =========================== Simulation model ===================================
    @authorized_method
    async def handle_simulation_model_created(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, _ = await self.task_service.create_user(user_id)
        msg = await self.task_service.get_variant_tasks_description(user, scip_completed=True)

        return {"msg": msg, "hint": msg}  # , "kb_id": data["result"]["knowledgeBase"]["id"]}

    @authorized_method
    async def handle_simulation_model_updated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)

    #   ============================= Resource Types ====================================
    @authorized_method
    async def handle_resource_type(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал тип ресурса (ИМ): ", data)
        task_object = SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(resource_type.name, task_object)

        if not task:
            # tasks = await self.task_service.get_variant_tasks_description(
            #     user, skip_completed=False, task_object=task_object
            # )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                # "hint": tasks
            }

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
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, task_object)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object = SUBJECT_CHOICES.SIMULATION_RESOURCES

                # tasks = await self.task_service.get_variant_tasks_description(
                #     user, skip_completed=False, task_object=task_object
                # )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    # "hint": tasks,
                    "skills": skills,
                }

            else:
                return await self.get_errors_result(errors_list, user, task, task_object)

    #   ==============================    Resource   ====================================
    @authorized_method
    async def handle_resource(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал ресурс (ИМ): ", data)
        task_object = SUBJECT_CHOICES.SIMULATION_RESOURCES
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            resource = await self.resource_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(resource.name, task_object)

        if not task:
            # tasks = await self.task_service.get_variant_tasks_description(
            #     user, skip_completed=False, task_object=task_object
            # )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                # "hint": tasks
            }

        else:
            self.add_im_resource_to_cash(resource, auth_token)

            print(task.object_name, task.object_reference, resource)

            resource_type_name = self.get_im_resource_type_from_cash(resource.resource_type_id, auth_token)
            print(f"Строка, полученная для сравнения: {resource_type_name}")

            errors_list = []
            errors_list_logic = await self.resource_service.handle_logic_mistakes(user_id, resource, resource_type_name)
            if errors_list_logic:
                errors_list.extend(errors_list_logic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 7)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object = SUBJECT_CHOICES.SIMULATION_TEMPLATES

                # tasks = await self.task_service.get_variant_tasks_description(
                #     user, skip_completed=False, task_object=task_object
                # )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    # "hint": tasks,
                    "skills": skills,
                }

            else:  # Преобразуем объекты CommonMistake в словари
                return await self.get_errors_result(errors_list, user, task, SUBJECT_CHOICES.SIMULATION_RESOURCES)

    #   =============================    Template   ================================
    @authorized_method
    async def handle_template(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал образец операции (ИМ): ", data)
        task_object = SUBJECT_CHOICES.SIMULATION_TEMPLATES
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            template = await self.template_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(template.meta.name, task_object)

        if not task:
            # tasks = await self.task_service.get_variant_tasks_description(
            #     user, skip_completed=False, task_object=task_object
            # )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                # "hint": tasks
            }

        else:
            self.add_im_template_to_cash(template.meta, auth_token)

            # print(task.object_name, task.object_reference, template)
            print(f"Данные, которые передаются для поиска ресурса: {template.meta.rel_resources}")

            resource_type_name = self.get_resource_type_names_from_cache(template.meta.rel_resources, auth_token)

            errors_list = []
            errors_list_logic = await self.template_service.handle_logic_mistakes(user_id, template, resource_type_name)
            errors_list_lexic = await self.template_service.handle_lexic_mistakes(user_id, template, resource_type_name)

            if errors_list_logic:
                errors_list.extend(errors_list_logic)
            if errors_list_lexic:
                errors_list.extend(errors_list_lexic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, task_object)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object = SUBJECT_CHOICES.SIMULATION_TEMPLATE_USAGES

                # tasks = await self.task_service.get_variant_tasks_description(
                #     user, skip_completed=False, task_object=task_object
                # )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    # "hint": tasks,
                    "skills": skills,
                }

            else:  # Преобразуем объекты CommonMistake в словари
                return await self.get_errors_result(errors_list, user, task, SUBJECT_CHOICES.SIMULATION_TEMPLATES)

    #   ============================= Template Usage ================================
    @authorized_method
    async def handle_template_usage(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал операцию (ИМ): ", data)
        task_object = SUBJECT_CHOICES.SIMULATION_TEMPLATE_USAGES
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            template_usage = await self.template_usage_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(template_usage.name, task_object)

        if not task:
            # tasks = await self.task_service.get_variant_tasks_description(
            #     user, skip_completed=False, task_object=task_object
            # )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                # "hint": tasks
            }
        else:
            print(task.object_name, task.object_reference, template_usage)

            resource_type_name = self.get_resource_names_from_cache(template_usage.arguments, auth_token)
            template_name = self.get_template_name_from_cache(template_usage.template_id, auth_token)

            errors_list = []
            errors_list_logic = await self.template_usage_service.handle_logic_mistakes(
                user_id, template_usage, resource_type_name, template_name
            )
            if errors_list_logic:
                errors_list.extend(errors_list_logic)

            print(f"Результат: {errors_list}")

            if not errors_list:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, task_object)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object = SUBJECT_CHOICES.SIMULATION_FUNCS

                # tasks = await self.task_service.get_variant_tasks_description(
                #     user, skip_completed=False, task_object=task_object
                # )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    # "hint": tasks,
                    "skills": skills,
                }

            else:
                return await self.get_errors_result(errors_list, user, task, task_object)

    #   =============================== Function =====================================
    @authorized_method
    async def handle_function(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал функцию (ИМ): ", data)
        task_object = SUBJECT_CHOICES.SIMULATION_FUNCS
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            function = await self.function_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(function.name, task_object)

        if not task:
            # tasks = await self.task_service.get_variant_tasks_description(
            #     user, skip_completed=False, task_object=task_object
            # )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                # "hint": tasks
            }

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
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, task_object)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)

                # tasks = await self.task_service.get_variant_tasks_description(
                #     user, skip_completed=False, task_object=task_object
                # )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    # "hint": tasks,
                    "skills": skills,
                }

            else:
                return await self.get_errors_result(errors_list, user, task, task_object)

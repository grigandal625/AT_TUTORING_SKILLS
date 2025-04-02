from asyncio.log import logger

from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import authorized_method

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.service.simulation.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.subservice.function.service import FunctionService
from at_tutoring_skills.core.service.simulation.subservice.resource.service import ResourceService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.service import ResourceTypeService
from at_tutoring_skills.core.service.simulation.subservice.template.service import TemplateService
from at_tutoring_skills.core.service.simulation.subservice.template_usage.service import TemplateUsageService
from at_tutoring_skills.core.task.service import TaskService


class SimulationService(ATComponent):
    main_task_service = None

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
                # defaults={
                #     'variant': default_variant
                # }
            )

            if created:
                logger.info(f"Created new user: {auth_token}")
            else:
                logger.debug(f"User already exists: {auth_token}")

            return user, created

        except Exception as e:
            logger.error(f"Error creating user {auth_token}: {str(e)}")
            raise

    #   ============================= Resource Types ================================
    @authorized_method
    async def handle_resource_type(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал тип ресурса (ИМ): ", data)
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.main_task_service.create_user(user_id)
        await self.main_task_service.create_user_skill_connection(user)
        user_id = user.pk
        # self.main_task_service.create_task_user_safe(task, user)

        # try:
        #     resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)
        # except BaseException as e:
        #     raise ValueError(f"Handle IM Resource Type Created: Syntax Mistakes: {e}") from e

        # task : Task = await self.main_task_service.get_task_by_name(resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES)
        # print(task.object_name, task.object_reference, resource_type)

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

        resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)

        # Получение задачи по имени типа ресурса
        task = await self.main_task_service.get_task_by_name(
            resource_type.name, SUBJECT_CHOICES.SIMULATION_RESOURCE_TYPES
        )
        print(task.object_name, task.object_reference)

        if task:
            # Обработка логических ошибок
            # Обработка логических ошибок
            logic_errors = await self.resource_type_service.handle_logic_mistakes(user_id, resource_type)
            if logic_errors:
                # Преобразуем объекты CommonMistake в словари
                serialized_logic_errors = [error.model_dump() for error in logic_errors]
                return {"status": "error", "message": "Logic mistakes", "errors": serialized_logic_errors}

            # Обработка лексических ошибок
            lexic_errors = await self.resource_type_service.handle_lexic_mistakes(user_id, resource_type)
            if lexic_errors:
                # Преобразуем объекты CommonMistake в словари
                serialized_lexic_errors = [error.model_dump() for error in lexic_errors]
                return {"status": "error", "message": "Lexic mistakes", "errors": serialized_lexic_errors}
            # Завершение задачи
            try:
                await self.main_task_service.complete_task(task, user)
            except BaseException as e:
                return {"status": "error", "message": "Complete Task Error", "error": str(e)}
        else:
            return {"status": "error", "message": "Task not found"}

        return {"status": "success", "message": "Resource type processed successfully"}

    #   =============================    Resource   =================================
    @authorized_method
    async def handle_resource(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал ресурс (ИМ): ", data)
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        user_id = user.pk
        # self.task_service.create_task_user_safe(task, user)

        try:
            resource = self.resource_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Syntax Mistakes: {e}") from e

        try:
            await self.resource_service.handle_logic_mistakes(user_id, resource)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Logic Mistakes: {e}") from e

        try:
            await self.resource_service.handle_lexic_mistakes(user_id, resource)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Lexic Mistakes: {e}") from e

        try:
            ITaskService.complete_task(user_id, event, resource.id)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Created: Complete Task: {e}") from e

    #   =============================    Template   ================================
    def handle_template(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал образец операции (ИМ): ", data)
        user_id = self.get_user_id_or_token(auth_token)
        try:
            template = TemplateService.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Syntax Mistakes: {e}") from e

        try:
            TemplateService.handle_logic_mistakes(user_id, template)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Logic Mistakes: {e}") from e

        try:
            TemplateService.handle_lexic_mistakes(user_id, template)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Lexic Mistakes: {e}") from e

        try:
            ITaskService.complete_task(user_id, event, template.id)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Created: Complete Task: {e}") from e

    #   ============================= Template Usage ================================
    def handle_template_usage(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал тип ресурса (ИМ): ", data)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            template_usage = TemplateUsageService.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Syntax Mistakes: {e}") from e

        try:
            TemplateUsageService.handle_logic_mistakes(user_id, template_usage)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Logic Mistakes: {e}") from e

        try:
            TemplateUsageService.handle_lexic_mistakes(user_id, template_usage)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Lexic Mistakes: {e}") from e

        try:
            ITaskService.complete_task(user_id, event, template_usage.id)
        except BaseException as e:
            raise ValueError(f"Handle IM Template Usage Created: Complete Task: {e}") from e

    #   ============================= Function =====================================
    @authorized_method
    async def handle_function(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал функцию (ИМ): ", data)
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.create_user(user_id)

        try:
            function = await self.function_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Syntax Mistakes: {e}") from e

        try:
            await self.function_service.handle_logic_mistakes(user_id, function)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Logic Mistakes: {e}") from e

        try:
            await self.function_service.handle_lexic_mistakes(user_id, function)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Lexic Mistakes: {e}") from e

        try:
            ITaskService.complete_task(user_id, event, function.id)
        except BaseException as e:
            raise ValueError(f"Handle IM Function Created: Complete Task: {e}") from e

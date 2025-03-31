from asyncio.log import logger
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method

from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.core.service.simulation.dependencies import ITaskService
from at_tutoring_skills.core.service.simulation.dependencies import IMistakeService
from at_tutoring_skills.core.service.simulation.subservice.function.service import FunctionService
from at_tutoring_skills.core.service.simulation.subservice.resource.service import ResourceService
from at_tutoring_skills.core.service.simulation.subservice.resource_type.service import ResourceTypeService
from at_tutoring_skills.core.service.simulation.subservice.template.service import TemplateService
from at_tutoring_skills.core.service.simulation.subservice.template_usage.service import TemplateUsageService


class SimulationService(ATComponent):

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
        user, created = await self.create_user(user_id)
        # await self.task_service.createUserSkillConnectionAsync(user)

        # kb_type, errors = await self.type_service.handle_syntax_mistakes(user_id, data)
        # if errors:
        # return errors

        try:
            resource_type = await self.resource_type_service.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Syntax Mistakes: {e}") from e
        
        try:
            self.resource_type_service.handle_logic_mistakes(user_id, resource_type) 
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Logic Mistakes: {e}") from e

        try:
            self.resource_type_service.handle_lexic_mistakes(user_id, resource_type)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Lexic Mistakes: {e}") from e

        try:
            ITaskService.complete_task(user_id, event, resource_type.id)
        except BaseException as e:
            raise ValueError(f"Handle IM Resource Type Created: Complete Task: {e}") from e
        

#   =============================    Resource   =================================
    @authorized_method
    async def handle_resource(self, event: str, data: dict, auth_token: int):
        print("Обучаемый отредактировал ресурс (ИМ): ", data)
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.create_user(user_id)

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
        user_id = self.get_user_id_or_token(self, auth_token)
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

from at_tutoring_skills.core.service.simulation.subservice.resource_type.service import ResourceTypeService
from at_tutoring_skills.core.service.simulation.subservice.template_usage.service import TemplateUsageService
from at_tutoring_skills.core.service.simulation.subservice.resource.service import ResourceService
from at_tutoring_skills.core.service.simulation.subservice.template.service import TemplateService
from at_tutoring_skills.core.service.simulation.subservice.function.service import FunctionService

from at_tutoring_skills.core.service.simulation.dependencies import ITaskService
# from at_tutoring_skills.core.task.service import ITaskService

class SimulationService:
    def __init__(
        self,
    ):
        pass

    async def get_user_id_or_token(self, auth_token: str) -> int | str:
        if await self.check_external_registered("AuthWorker"):
            user_id = await self.exec_external_method(
                reciever="AuthWorker",
                methode_name="verify_token",
                method_args={"token": auth_token},
            )
            return user_id
        return auth_token


    def handle_resource_type(self, event: str, resource_type_raw: dict, user_id: int) -> None:
        # pass
        print("Обучаемый отредактировал тип ресурса (ИМ): ", resource_type_raw)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            resource_type = ResourceTypeService.handle_syntax_mistakes(user_id, resource_type_raw)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Type Created: Syntax Mistakes: {e}"
            ) from e

        try:
            ResourceTypeService.handle_logic_mistakes(user_id, resource_type)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Type Created: Logic Mistakes: {e}"
            ) from e
        
        try:
            ResourceTypeService.handle_lexic_mistakes(user_id, resource_type)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Type Created: Lexic Mistakes: {e}"
            ) from e

        try:
            ITaskService.complete_task(user_id, event, resource_type.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e



    def handle_resource(self, event: str, resource_raw: dict, user_id: int) -> None: 
        print("Обучаемый отредактировал тип ресурса (ИМ): ", resource_raw)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            resource = ResourceService.handle_syntax_mistakes(user_id, resource_raw)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Created: Syntax Mistakes: {e}"
            ) from e

        try:
            ResourceService.handle_logic_mistakes(user_id, resource)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Created: Logic Mistakes: {e}"
            ) from e
        
        try:
            ResourceService.handle_lexic_mistakes(user_id, resource)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Resource Created: Lexic Mistakes: {e}"
            ) from e
    
        try:
            ITaskService.complete_task(user_id, event, resource.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e



    def handle_template(self, event: str, template_raw: dict, user_id: int) -> None: 
        print("Обучаемый отредактировал тип ресурса (ИМ): ", template_raw)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            template = TemplateService.handle_syntax_mistakes(user_id, template_raw)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Created: Syntax Mistakes: {e}"
            ) from e

        try:
            TemplateService.handle_logic_mistakes(user_id, template)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Created: Logic Mistakes: {e}"
            ) from e
        
        try:
            TemplateService.handle_lexic_mistakes(user_id, template)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Created: Lexic Mistakes: {e}"
            ) from e
    
        try:
            ITaskService.complete_task(user_id, event, template.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e



    def handle_template_usage(self, event: str, template_usage_raw: dict, user_id: int) -> None: 
        print("Обучаемый отредактировал тип ресурса (ИМ): ", template_usage_raw)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            template_usage = TemplateUsageService.handle_syntax_mistakes(user_id, template_usage_raw)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Usage Created: Syntax Mistakes: {e}"
            ) from e

        try:
            TemplateUsageService.handle_logic_mistakes(user_id, template_usage)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Usage Created: Logic Mistakes: {e}"
            ) from e
        
        try:
            TemplateUsageService.handle_lexic_mistakes(user_id, template_usage)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Template Usage Created: Lexic Mistakes: {e}"
            ) from e
    
        try:
            ITaskService.complete_task(user_id, event, template_usage.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e



    def handle_function(self, event: str, function_raw: dict, user_id: int) -> None: 
        print("Обучаемый отредактировал тип ресурса (ИМ): ", function_raw)
        user_id = self.get_user_id_or_token(self, user_id)
        try:
            function = FunctionService.handle_syntax_mistakes(user_id, function_raw)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Function Created: Syntax Mistakes: {e}"
            ) from e

        try:
            FunctionService.handle_logic_mistakes(user_id, function)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Function Created: Logic Mistakes: {e}"
            ) from e
        
        try:
            FunctionService.handle_lexic_mistakes(user_id, function)
        except BaseException as e:
            raise ValueError(
                f"Handle IM Function Created: Lexic Mistakes: {e}"
            ) from e
    
        try:
            ITaskService.complete_task(user_id, event, function.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e


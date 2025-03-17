class SimulationService:
    def __init__(
        self,
    ):
        pass

    def handle_resource_type(self, resource_type_raw: dict, user_id: int) -> None:
        pass
        # try:
        #     template_usage = IMTemplateUsageService.handle_syntax_mistakes(
        #         user_id, data
        #     )
        # except BaseException as e:
        #     raise ValueError(
        #         f"Handle IM Template Usage Created: Syntax Mistakes: {e}"
        #     ) from e

        # try:
        #     IMTemplateUsageService.handle_logic_mistakes(user_id, template_usage)
        # except BaseException as e:
        #     raise ValueError(
        #         f"Handle IM Template Usage Created: Logic Mistakes: {e}"
        #     ) from e

        # try:
        #     TaskService.complete_task(user_id, event, template_usage.id)
        # except BaseException as e:
        #     raise ValueError(
        #         f"Handle IM Template Usage Created: Complete Task: {e}"
        #     ) from e

    def handle_resource(self, resource_raw: dict, user_id: int) -> None: ...

    def handle_template(self, template_raw: dict, user_id: int) -> None: ...

    def handle_template_usage(self, template_usage_raw: dict, user_id: int) -> None: ...

    def handle_function(self, function_raw: dict, user_id: int) -> None: ...

from typing import Protocol


class ISimulationService(Protocol):
    def handle_resource_type(self, resource_type_raw: dict, user_id: int) -> None:
        ...

    def handle_resource(self, resource_raw: dict, user_id: int) -> None:
        ...

    def handle_template(self, template_raw: dict, user_id: int) -> None:
        ...

    def handle_template_usage(self, template_usage_raw: dict, user_id: int) -> None:
        ...

    def handle_function(self, function_raw: dict, user_id: int) -> None:
        ...


class IAuthClient(Protocol):
    async def verify_token(self, token: str) -> int:
        ...

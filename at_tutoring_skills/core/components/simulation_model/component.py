from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import authorized_method

from at_tutoring_skills.core.components.simulation_model.dependencies import IAuthClient
from at_tutoring_skills.core.components.simulation_model.dependencies import ISimulationService


class ATTutoringSimulation(ATComponent):
    def __init__(
        self,
        connection_parameters,
        auth_client: IAuthClient,
        service: ISimulationService,
    ):
        super().__init__(connection_parameters=connection_parameters)
        self._auth_client = auth_client
        self._service = service

    @authorized_method
    async def handle_resource_type(
        self,
        event: str,
        data: dict,
        auth_token: str,
    ) -> None:
        user_id = self._auth_client.verify_token(auth_token)
        self._service.handle_resource_type(data, user_id)

    @authorized_method
    async def handle_resource(self, event: str, data: dict, auth_token: str) -> None:
        user_id = self._auth_client.verify_token(auth_token)
        self._service.handle_resource(data, user_id)

    @authorized_method
    async def handle_template(self, event: str, data: dict, auth_token: str) -> None:
        user_id = self._auth_client.verify_token(auth_token)
        self._service.handle_template(data, user_id)

    @authorized_method
    async def handle_template_usage(self, event: str, data: dict, auth_token: str) -> None:
        user_id = self._auth_client.verify_token(auth_token)
        self._service.handle_template_usage(data, user_id)

    @authorized_method
    async def handle_function(self, event: str, data: dict, auth_token: str) -> None:
        user_id = self._auth_client.verify_token(auth_token)
        self._service.handle_function(data, user_id)

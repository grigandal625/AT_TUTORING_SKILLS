from adrf import viewsets
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.filters import ByAuthTokenFilter
from at_tutoring_skills.apps.skills.serializers import QueryParamSerializer
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills
from rest_framework.decorators import action
from at_tutoring_skills.core.task.skill_service import SkillService
from at_queue.core.exceptions import ExternalMethodException
from rest_framework import exceptions


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    user_id: str | int
    lookup_field = 'user_id'
    
    filter_backends = [ByAuthTokenFilter]

    async def get_user_id(self):
        self.serializer = QueryParamSerializer(data=self.request.query_params)
        await self.serializer.ais_valid(raise_exception=True)
        auth_token = self.serializer.data.get("auth_token")

        kb_skills: ATTutoringKBSkills = self.request.scope["kb_skills"]
        try:
            result = await kb_skills.get_user_id_or_token(auth_token=auth_token)
            return str(result)
        except ExternalMethodException as e:
            if 'Invalid token' in e.args[-1].get('errors', [''])[-1]:
                raise exceptions.AuthenticationFailed()
            raise e

    @action(detail=False, methods=["GET"])
    async def skills_graph(self, request):
        
        self.user_id = await self.get_user_id()
        self.kwargs = {"user_id": self.user_id}
        user: User = await self.aget_object()
        task_object = self.serializer.data.get('task_object')

        service = SkillService()
        skills = await service.process_and_get_skills(user, task_object)
        


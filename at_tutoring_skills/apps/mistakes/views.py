# Create your views here.
from at_tutoring_skills.apps.mistakes.models import Mistake

from adrf import mixins
from adrf import viewsets

from at_tutoring_skills.apps.mistakes.serializers import MistakeSerializer
from at_tutoring_skills.apps.skills.filters import ByAuthTokenFilter, MistakeFilter
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.serializers import QueryParamSerializer
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills
from at_queue.core.exceptions import ExternalMethodException
from rest_framework import exceptions
from django_filters.rest_framework import DjangoFilterBackend


class MistakeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Mistake.objects.all()
    serializer_class = MistakeSerializer
    filter_backends = [ByAuthTokenFilter, DjangoFilterBackend]
    filterset_class = MistakeFilter

    async def get_user(self) -> User:
        """Получение пользователя по auth-токену"""
        serializer = QueryParamSerializer(data=self.request.query_params)
        await serializer.ais_valid(raise_exception=True)
        auth_token = serializer.data.get("auth_token")

        kb_skills: ATTutoringKBSkills = self.request.scope["kb_skills"]
        try:
            user_id = await kb_skills.get_user_id_or_token(auth_token=auth_token)
            return await User.objects.aget(user_id=str(user_id))
        except ExternalMethodException as e:
            if "Invalid token" in e.args[-1].get("errors", [""])[-1]:
                raise exceptions.AuthenticationFailed()
            raise e

    async def aupdate(self, *args, **kwargs):
        user = await self.get_user()
        self.user_id = user.user_id
        return await super().aupdate(*args, **kwargs)

    async def alist(self, *args, **kwargs):
        user = await self.get_user()
        self.user_id = user.user_id
        return await super().alist(*args, **kwargs)


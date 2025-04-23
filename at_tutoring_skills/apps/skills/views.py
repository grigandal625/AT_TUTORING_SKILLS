from adrf import viewsets
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.serializers import UserSerializer
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    async def alist(self, *args, **kwargs):
        kb_skills: ATTutoringKBSkills = self.request.scope.get("kb_skills")
        at_solver_registered = await kb_skills.check_external_registered('ATSolver')
        assert at_solver_registered, "ATSolver is not registered"

        return await super().alist(*args, **kwargs)
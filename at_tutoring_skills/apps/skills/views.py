from adrf import viewsets
from at_tutoring_skills.apps.skills.models import User, UserSkill, SKillConnection
from at_tutoring_skills.apps.skills.filters import ByAuthTokenFilter
from at_tutoring_skills.apps.skills.serializers import QueryParamSerializer
from at_tutoring_skills.core.KBskills import ATTutoringKBSkills
from rest_framework.decorators import action
from at_tutoring_skills.core.task.skill_service import SkillService
from at_queue.core.exceptions import ExternalMethodException
from rest_framework import exceptions
from at_tutoring_skills.apps.skills import dto
from at_tutoring_skills.apps.skills import graph
import tempfile
from django.http import HttpResponse
import os

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
        
    async def get_dto(self):
        self.user_id = await self.get_user_id()
        self.kwargs = {"user_id": self.user_id}
        user: User = await self.aget_object()
        task_object = self.serializer.data.get('task_object')
        as_initial = self.serializer.data.get('as_initial', False)

        service = SkillService()
        user_skills_list = await service.process_and_get_skills(user, task_object)
        user_skills = UserSkill.objects.filter().select_related('skill').filter(pk__in=[
            us.pk for us in user_skills_list
        ])

        dto_skills: list[dto.Skill] = []
        dto_relations: list[dto.SkillRelation] = []
        dto_user_skills: list[dto.UserSkill] = []

        async for user_skill in user_skills:
            dto_user_skills.append(dto.UserSkill(
                pk=user_skill.pk, 
                user_id=user_skill.user_id, 
                skill_id=user_skill.skill_id,
                mark=user_skill.mark if not as_initial else 0,
            ))
            dto_skills.append(
                dto.Skill(
                    pk=user_skill.skill.pk, 
                    name=user_skill.skill.name, 
                    group=user_skill.skill.group,
                    code=user_skill.skill.code,
                )
            )
        availible_skills = [s.pk for s in dto_skills]
        relations = SKillConnection.objects.filter(skill_from_id__in=availible_skills, skill_to_id__in=availible_skills)

        async for relation in relations:
            dto_relations.append(dto.SkillRelation(
                pk=relation.pk, 
                source_skill_id=relation.skill_from_id, 
                target_skill_id=relation.skill_to_id,
                relation_type=relation.weight
            ))

        return dto_skills, dto_relations, dto_user_skills

    @action(detail=False, methods=["GET"])
    async def skills_graph(self, *args, **kwargs):
        skills, relations, user_skills = await self.get_dto()
        dot = graph.build_skill_graph(skills, relations, user_skills)
        dot.format = "png"
        with tempfile.TemporaryDirectory() as tmp_dir:
        
            file_path = os.path.join(tmp_dir, 'graph')
            dot.render(file_path, cleanup=True)
            
            with open(file_path + '.png', 'rb') as f:
                image_data = f.read()
        
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="graph.png"'
        return response
    
    @action(detail=False, methods=["GET"])
    async def skills_graph_legend(self, *args, **kwargs):
        skills, relations, user_skills = await self.get_dto()
        dot = graph.build_legend_graph(skills, relations, user_skills)
        dot.format = "png"
        with tempfile.TemporaryDirectory() as tmp_dir:
        
            file_path = os.path.join(tmp_dir, 'graph')
            dot.render(file_path, cleanup=True)
            
            with open(file_path + '.png', 'rb') as f:
                image_data = f.read()
        
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="graph.png"'
        return response
        


        
        
            





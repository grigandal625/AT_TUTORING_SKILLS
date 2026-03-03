from at_tutoring_skills.apps.skills.models import Skill, Competence, SkillCompetence, User, UserSkill, UserCompetence
from asgiref.sync import sync_to_async
from typing import List

class ComptenceService:
    def __init__(self):
        pass

    @sync_to_async
    def _calc_competence(self, user: User, competence: Competence):
        user_competence = UserCompetence.objects.filter(user=user, competence=competence)
        user_skills = list(UserSkill.objects.filter(user=user))
        skill_competence = list(SkillCompetence.objects.all(competence=competence))

        weght, total_weight = 0, 0
        for skill in user_skills:
            for sc in skill_competence:
                if sc.skill == skill.skill:
                    weight += sc.weight*skill.mark
                    total_weight += sc.weight
                    break
        user_competence.mark = weight/total_weight
        user_competence.save()
        return user_competence.mark 

    async def calc_competence(self, user: User, competence: Competence):
        return await self._calc_competence(user, competence)
  
    @sync_to_async
    def _calc_competences(self, user: User):
        user_competences = list(UserCompetence.objects.filter(user=user))
        for competence in user_competences:
            competence.mark =  self._calc_competence(user, competence.competence)
            competence.save()

    async def calc_competences(self, user: User):
        return await self._calc_competences(user)


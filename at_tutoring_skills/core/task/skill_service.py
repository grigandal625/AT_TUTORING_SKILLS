from typing import List, Dict, Optional, Union
from asgiref.sync import sync_to_async
from django.db.models import F, Sum, Q
from django.contrib.auth import get_user_model
from at_tutoring_skills.apps.skills.models import (
    User, Skill, UserSkill, SKillConnection, Task, SUBJECT_CHOICES
)
from at_tutoring_skills.apps.mistakes.models import Mistake


class SkillService:
    def __init__(self):
        pass

    # Методы для работы с ошибками и базовыми оценками
    @sync_to_async
    def _calc_skill(self, user, skill):
        user_skill = UserSkill.objects.get(user=user, skill=skill)
        mistakes = list(Mistake.objects.filter(
            user=user, 
            skills__in=[skill]
        ).exclude(fine__isnull=True))
        
        total_fine = sum(mistake.fine for mistake in mistakes)
        user_skill.mark = max(0, 100 - total_fine)
        user_skill.save()
        return user_skill.mark

    async def calc_skill(self, user: User, skill: Skill) -> float:
        return await self._calc_skill(user, skill)

    # Методы для получения навыков пользователя
    @sync_to_async
    def _get_user_skills_direct(self, user, task=None):
        result = UserSkill.objects.filter(user=user)
        if task:
            result = result.filter(skill__mistake__task=task)
        return list(result.select_related("skill").distinct())

    async def get_user_task_skills(self, user: User, task: Task = None) -> List[UserSkill]:
        return await self._get_user_skills_direct(user, task)

    @sync_to_async
    def _get_user_task_skills_for_first_codes(self, user, first_codes):
        result = UserSkill.objects.filter(user=user)
        query = Q()
        for first_code in first_codes:
            query |= Q(skill__code__gte=first_code * 10, 
                      skill__code__lt=(first_code + 10) * 10)
        result = result.filter(query)
        return list(result.select_related("skill").distinct())

    async def get_user_task_skills_for_first_codes(self, user: User, 
                                                 first_codes: List[int]) -> List[UserSkill]:
        return await self._get_user_task_skills_for_first_codes(user, first_codes)

    # Методы для работы с целевыми навыками (skill_to)
    @sync_to_async
    def _get_target_skills(self):
        return list(Skill.objects.filter(skill_to__isnull=False).distinct())

    async def get_target_skills(self) -> List[Skill]:
        return await self._get_target_skills()

    @sync_to_async
    def _can_calculate_skill(self, user, skill):
        source_skills = SKillConnection.objects.filter(
            skill_to=skill
        ).values_list('skill_from', flat=True)
        existing_skills_count = UserSkill.objects.filter(
            user=user,
            skill__in=source_skills
        ).count()
        return existing_skills_count == len(source_skills)

    async def can_calculate_skill(self, user: User, skill: Skill) -> bool:
        return await self._can_calculate_skill(user, skill)

    @sync_to_async
    def _calculate_weighted_mark(self, user, skill):
        connections = SKillConnection.objects.filter(skill_to=skill)
        result = UserSkill.objects.filter(
            user=user,
            skill__in=connections.values('skill_from')
        ).annotate(
            weighted=F('mark') * F('skill__skill_from__weight')
        ).aggregate(
            total_weighted=Sum('weighted'),
            total_weights=Sum('skill__skill_from__weight')
        )
        return (result['total_weighted'] / result['total_weights']) if result['total_weights'] else None

    async def calculate_weighted_mark(self, user: User, skill: Skill) -> Optional[float]:
        return await self._calculate_weighted_mark(user, skill)

    @sync_to_async
    def _update_user_skill(self, user, skill, mark):
        user_skill, _ = UserSkill.objects.update_or_create(
            user=user,
            skill=skill,
            defaults={'mark': mark}
        )
        return user_skill

    async def iterative_update_user_skills(self, user: User, max_iterations: int = 100) -> Dict:
        iterations = 0
        total_updated = 0
        
        while iterations < max_iterations:
            iterations += 1
            updated_in_iteration = 0
            
            target_skills = await self.get_target_skills()
            
            for skill in target_skills:
                if not await self.can_calculate_skill(user, skill):
                    continue
                
                weighted_mark = await self.calculate_weighted_mark(user, skill)
                if weighted_mark is None:
                    continue
                
                user_skill = await sync_to_async(UserSkill.objects.get)(
                    user=user,
                    skill=skill
                )
                
                if abs(user_skill.mark - weighted_mark) > 0.001:
                    await self._update_user_skill(user, skill, weighted_mark)
                    updated_in_iteration += 1
            
            total_updated += updated_in_iteration
            
            if updated_in_iteration == 0:
                return {
                    'iterations': iterations,
                    'updated': total_updated,
                    'converged': True
                }
        
        return {
            'iterations': iterations,
            'updated': total_updated,
            'converged': False
        }

    # Методы для обработки и вывода результатов
    async def process_and_get_skills_string(
        self, 
        user: User, 
        task_object: Union[int, SUBJECT_CHOICES, List[Union[int, SUBJECT_CHOICES]]] = None
    ) -> str:
        if not isinstance(task_object, list) and task_object is not None:
            task_object = [task_object]

        if task_object is not None:
            codes = set()
            for subject in task_object:
                codes |= set(SUBJECT_CHOICES.get_first_codes(subject=subject))
            skills = await self.get_user_task_skills_for_first_codes(user, list(codes))
        else:
            skills = await self.get_user_task_skills(user)

        for skill in skills:
            await self.calc_skill(user, skill.skill)
            await self.iterative_update_user_skills(user)

        if task_object is not None :
            updated_skills = await self.get_user_task_skills_for_first_codes(user, list(codes))                 
        else: updated_skills = await self.get_user_task_skills(user)

        return "\n\n".join(f"{us.skill.name} : {us.mark}" for us in updated_skills)

    async def complete_skills_stage_done(
        self, 
        user: User, 
        task_object: Union[int, SUBJECT_CHOICES, List[Union[int, SUBJECT_CHOICES]]] = None
    ) -> str:
        if not isinstance(task_object, list):
            task_object = [task_object]

        codes = set()
        for subject in task_object:
            codes |= set(SUBJECT_CHOICES.get_first_codes(subject=subject))

        skills = await self.get_user_task_skills_for_first_codes(user, list(codes))

        for skill in skills:
            skill.is_completed = True
            skill.mark = min(60, skill.mark)
            await sync_to_async(skill.save)()

        updated_skills = await self.get_user_task_skills_for_first_codes(user, list(codes))
        return "\n\n".join(f"{us.skill.name} : {us.mark}" for us in updated_skills)

    # Вспомогательные методы
    @sync_to_async
    def _get_uncalculated_skills(self, user):
        target_skills = Skill.objects.filter(skill_to__isnull=False)
        return [
            skill for skill in target_skills
            if not self._can_calculate_skill(user, skill)
        ]

    async def get_uncalculated_skills(self, user: User) -> List[Skill]:
        return await self._get_uncalculated_skills(user)

    @sync_to_async
    def _get_skill_dependencies(self, skill):
        return list(Skill.objects.filter(
            id__in=SKillConnection.objects.filter(
                skill_to=skill
            ).values('skill_from')
        ))

    async def get_skill_dependencies(self, skill: Skill) -> List[Skill]:
        return await self._get_skill_dependencies(skill)
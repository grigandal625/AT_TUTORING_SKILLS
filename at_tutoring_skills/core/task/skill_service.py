from typing import List

from asgiref.sync import sync_to_async
from django.db.models import Q

from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.models import UserSkill


class SkillService:
    def __init__(self):
        pass

    async def calc_skill(self, user: User, skill: Skill) -> bool:
        # Get the UserSkill instance for this user and skill
        user_skill = await sync_to_async(UserSkill.objects.get)(user=user, skill=skill)

        # Get all mistakes for this user that are related to the skill
        mistakes = await sync_to_async(
            lambda: list(Mistake.objects.filter(user=user, skills__in=[skill]).exclude(fine__isnull=True))
        )()

        # Calculate total fine
        total_fine = sum(mistake.fine for mistake in mistakes)

        # Update the UserSkill mark
        user_skill.mark = max(0, 100 - total_fine)  # Ensure mark doesn't go below 0

        # Save the updated UserSkill
        await sync_to_async(user_skill.save)()

        return user_skill.mark

    @sync_to_async
    def _get_user_skills_direct(self, user, task=None):
        result = UserSkill.objects.filter(user=user)
        if task:
            result = result.filter(skill__mistake__task=task)

        return list(result.select_related("skill").distinct())

    async def get_user_task_skills(self, user: User, task: Task = None) -> list[UserSkill]:
        return await self._get_user_skills_direct(user, task)

    @sync_to_async
    def _get_user_task_skills_for_first_codes(self, user: User, first_codes: List[int]) -> list[UserSkill]:
        """
        Получает навыки пользователя для задания по заданной сущности, указываемой в заданиях
        """

        result = UserSkill.objects.filter(user=user)

        query = Q()

        for first_code in first_codes:
            query |= Q(skill__code__gte=first_code * 10, skill__code__lt=(first_code + 10) * 10)

        result = result.filter(query)

        return list(result.select_related("skill").distinct())

    async def get_user_task_skills_for_first_codes(self, user: User, first_codes: List[int]) -> list[UserSkill]:
        return await self._get_user_task_skills_for_first_codes(user, first_codes)

    async def process_and_get_skills_string(
        self, user: User, task_object: int | SUBJECT_CHOICES | List[int | SUBJECT_CHOICES] = None
    ) -> str:
        """
        Обрабатывает навыки пользователя для задания и возвращает строку с результатами
        """

        if not isinstance(task_object, list):
            task_object = [task_object]

        codes = set()
        for subject in task_object:
            codes |= set(SUBJECT_CHOICES.get_first_codes(subject=subject))

        skills = await self.get_user_task_skills_for_first_codes(user, first_codes=list(codes))

        # 2. Пересчитываем оценку для каждого навыка
        for skill in skills:
            await self.calc_skill(user, skill.skill)

        # 3. Получаем обновленные навыки после пересчета
        updated_skills = await self.get_user_task_skills_for_first_codes(user, first_codes=list(codes))

        # 4. Формируем итоговую строку
        return "\n\n".join(f"{us.skill.name} : {us.mark}" for us in updated_skills)

    async def complete_skills_stage_done(
        self, user: User, task_object: int | SUBJECT_CHOICES | List[int | SUBJECT_CHOICES] = None
    ) -> str:
        """
        Обрабатывает навыки пользователя для задания и возвращает строку с результатами
        """

        if not isinstance(task_object, list):
            task_object = [task_object]

        codes = set()
        for subject in task_object:
            codes |= set(SUBJECT_CHOICES.get_first_codes(subject=subject))

        skills = await self.get_user_task_skills_for_first_codes(user, first_codes=list(codes))

        # 2. Пересчитываем оценку для каждого навыка
        for skill in skills:
            skill.is_completed = True
            skill.mark = min(60, skill.mark)
            await skill.asave()

        # 3. Получаем обновленные навыки после пересчета
        updated_skills = await self.get_user_task_skills_for_first_codes(user, first_codes=list(codes))

        # 4. Формируем итоговую строку
        return "\n\n".join(f"{us.skill.name} : {us.mark}" for us in updated_skills)

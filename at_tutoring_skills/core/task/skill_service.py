from asgiref.sync import sync_to_async

from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.models import Skill
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
        user_skill.mark = max(0, user_skill.mark - total_fine)  # Ensure mark doesn't go below 0

        # Save the updated UserSkill
        await sync_to_async(user_skill.save)()

        return user_skill.mark

    @sync_to_async
    def _get_user_skills_direct(self, user, task):
        return list(
            UserSkill.objects.filter(user=user, skill__mistake__user=user, skill__mistake__task=task)
            .select_related("skill")
            .distinct()
        )

    async def get_user_task_skills(self, user: User, task: Task) -> list[UserSkill]:
        return await self._get_user_skills_direct(user, task)

    async def process_and_get_skills_string(self, user: User, task: Task) -> str:
        """
        Обрабатывает навыки пользователя для задания и возвращает строку с результатами

        Шаги:
        1. Получает навыки пользователя для задания
        2. Пересчитывает оценку для каждого навыка
        3. Получает обновленные навыки
        4. Формирует строку с результатами

        Args:
            user: Объект пользователя
            task: Объект задания

        Returns:
            Строка с навыками и оценками в формате "навык : оценка"
        """
        # 1. Получаем начальные навыки
        skills = await self.get_user_task_skills(user, task)

        # 2. Пересчитываем оценку для каждого навыка
        for skill in skills:
            await self.calc_skill(user, skill.skill)

        # 3. Получаем обновленные навыки после пересчета
        updated_skills = await self.get_user_task_skills(user, task)

        # 4. Формируем итоговую строку
        return "\n".join(f"{us.skill.name} : {us.mark}" for us in updated_skills)

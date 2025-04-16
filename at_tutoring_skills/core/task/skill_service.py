from venv import logger

from asgiref.sync import sync_to_async

from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import User
from at_tutoring_skills.apps.skills.models import UserSkill


class SkillService:
    def __init__(self):
        pass

    async def calc_skill(self, user: User, skill: Skill) -> bool:
        try:
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

            return True

        except UserSkill.DoesNotExist:
            logger.error(f"UserSkill not found for user {user.id} and skill {skill.id}")
            return False
        except Exception as e:
            logger.error(f"Error in calc_skill: {str(e)}")
            return False

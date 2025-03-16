from adrf import serializers

from at_tutoring_skills.apps.skills.models import Skill
from at_tutoring_skills.apps.skills.models import Task


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

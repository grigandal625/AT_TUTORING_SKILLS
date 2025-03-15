# project/skills_data/ATskills/serializers.py
from rest_framework import serializers

from .models import Event
from .models import Reaction
from .models import ScenarioPart
from .models import Skill
from .models import Task


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = "__all__"


class ScenarioPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioPart
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

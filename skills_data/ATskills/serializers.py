# project/skills_data/ATskills/serializers.py
from rest_framework import serializers
from .models import Skill, Task, Reaction, ScenarioPart, Event

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'

class ScenarioPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioPart
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
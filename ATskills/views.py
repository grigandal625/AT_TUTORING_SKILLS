
from django.shortcuts import render
#-
# Create your views here.#-
# project/skills_data/ATskills/views.py#-
# import rest_framework
from rest_framework import viewsets
from .models import Skill, Task, Reaction, ScenarioPart, Event
from .serializers import SkillSerializer, TaskSerializer, ReactionSerializer, ScenarioPartSerializer, EventSerializer

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

class ScenarioPartViewSet(viewsets.ModelViewSet):
    queryset = ScenarioPart.objects.all()
    serializer_class = ScenarioPartSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
# {"conversationId":"a3308710-35cf-4756-96f5-a44e5f818851","source":"instruct"}

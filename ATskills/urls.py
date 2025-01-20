# project/skills_data/ATskills/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SkillViewSet, TaskViewSet, ReactionViewSet, ScenarioPartViewSet, EventViewSet

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'reactions', ReactionViewSet)
router.register(r'scenario_parts', ScenarioPartViewSet)
router.register(r'events', EventViewSet)

urlpatterns = router.urls

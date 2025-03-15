# project/skills_data/ATskills/urls.py
from rest_framework.routers import DefaultRouter

from .views import EventViewSet
from .views import ReactionViewSet
from .views import ScenarioPartViewSet
from .views import SkillViewSet
from .views import TaskViewSet

router = DefaultRouter()
router.register(r"skills", SkillViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"reactions", ReactionViewSet)
router.register(r"scenario_parts", ScenarioPartViewSet)
router.register(r"events", EventViewSet)

urlpatterns = router.urls

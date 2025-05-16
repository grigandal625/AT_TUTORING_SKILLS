from typing import TYPE_CHECKING
from typing import Union

from django.db.models import QuerySet
from rest_framework.filters import BaseFilterBackend
from drf_spectacular.extensions import OpenApiFilterExtension

if TYPE_CHECKING:
    from at_tutoring_skills.apps.skills.views import UserViewSet, TaskUserViewSet
    from at_tutoring_skills.apps.skills.models import User, TaskUser


class ByAuthTokenFilter(BaseFilterBackend):
    required_for_detail = True
    
    def filter_queryset(
        self,
        request,
        queryset: Union[QuerySet["User"], QuerySet["TaskUser"]],
        view: Union["UserViewSet", "TaskUserViewSet"],
    ):
        user_id = view.user_id
        return queryset.filter(user_id=user_id)


class ByAuthTokenFilterExtension(OpenApiFilterExtension):
    target_class = "at_tutoring_skills.apps.skills.filters.ByAuthTokenFilter"

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        return [
            {
                "name": "auth_token",
                "in": "query",
                "required": True,
                "description": "Authentication token to filter by user",
                "schema": {
                    "type": "string",
                    "example": "abc123def456"
                },
                "style": "form",
                "explode": False
            }
        ]
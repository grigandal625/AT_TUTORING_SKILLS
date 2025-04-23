from rest_framework.filters import BaseFilterBackend
from typing import TYPE_CHECKING
from django.db.models import QuerySet

if TYPE_CHECKING:
    from at_tutoring_skills.apps.skills.views import UserViewSet
    from at_tutoring_skills.apps.skills.models import User


class ByAuthTokenFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset: QuerySet["User"], view: "UserViewSet"):
        user_id = view.user_id
        return queryset.filter(user_id=user_id)

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'auth_token',
                'in': 'query',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
        ]
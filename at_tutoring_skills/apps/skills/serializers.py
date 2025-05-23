from adrf import serializers
from rest_framework.fields import empty

from at_tutoring_skills.apps.skills.models import Task, User, Variant
from at_tutoring_skills.apps.skills.models import TaskUser


class OptionalQueryListField(serializers.ListField):
    async def arun_validation(self, data=empty):
        if data is empty:
            data = self.default
        return await super().arun_validation(data)


class QueryParamSerializer(serializers.Serializer):
    auth_token = serializers.CharField(error_messages={"required": "Query parameter is required"})
    task_object = OptionalQueryListField(child=serializers.IntegerField(), required=False, default=[])
    as_initial = serializers.BooleanField(required=False, default=False)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskUserSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskUser
        fields = "__all__"

class VariantSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Variant
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)
    class Meta:
        model = User
        fields = "__all__"

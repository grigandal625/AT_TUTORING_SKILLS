from adrf import serializers

from at_tutoring_skills.apps.skills.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class QueryParamSerializer(serializers.Serializer):
    auth_token = serializers.CharField(error_messages={'required': 'Query parameter is required'})
    task_object = serializers.ListField(child=serializers.IntegerField(), required=False, default=None)
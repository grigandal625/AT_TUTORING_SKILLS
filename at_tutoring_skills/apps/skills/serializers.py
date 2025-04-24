from adrf import serializers

from rest_framework.fields import empty


class OptionalQueryListField(serializers.ListField):

    async def arun_validation(self, data=empty):
        if data is empty:
            data = self.default
        return await super().arun_validation(data)
    


class QueryParamSerializer(serializers.Serializer):
    auth_token = serializers.CharField(error_messages={'required': 'Query parameter is required'})
    task_object = OptionalQueryListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )
    as_initial = serializers.BooleanField(required=False, default=False)
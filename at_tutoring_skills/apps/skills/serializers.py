from adrf import serializers

from at_tutoring_skills.apps.skills.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

from adrf import serializers
from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.serializers import TaskSerializer


class MistakeSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Mistake
        fields = "__all__"





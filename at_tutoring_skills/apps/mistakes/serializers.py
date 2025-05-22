from adrf import serializers
from at_tutoring_skills.apps.mistakes.models import Mistake
from at_tutoring_skills.apps.skills.serializers import TaskSerializer


class MistakeSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Mistake
        fields = "__all__"
        read_only_fields = [f.name for f in  Mistake._meta.fields if f.name != "is_tip_shown"] + ["skills"]





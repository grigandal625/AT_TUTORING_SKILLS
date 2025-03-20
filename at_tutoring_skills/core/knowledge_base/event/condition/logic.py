from typing import TYPE_CHECKING


from at_krl.core.kb_instruction import KBInstruction
from at_krl.core.kb_value import Evaluatable

from at_tutoring_skills.core.data_serializers import KBEventDataSerializer
from at_tutoring_skills.core.errors.context import Context 
from at_tutoring_skills.core.errors.context import StudentMistakeException 
from at_tutoring_skills.core.errors.conversions import to_logic_mistake
from at_tutoring_skills.core.errors.models import CommonMistake


class KBConditionServiceLogicLexic:

    def estimate_condition(self, condition_et: Evaluatable, condition: Evaluatable):
        errors_list = []
        pass
    def estimate_instruction(self, instruction_et: KBInstruction, instruction: KBInstruction):
        errors_list = []
        
        pass

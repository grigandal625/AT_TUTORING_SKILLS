# Create your tests here.
import json

from asgiref.sync import async_to_sync
from at_krl.models.kb_rule import KBRuleModel
from at_krl.utils.context import Context as ATKRLContext
from django.test import TestCase

from at_tutoring_skills.apps.skills.management.commands.importkb import Command as ImportKbCommand
from at_tutoring_skills.core.knowledge_base.condition.lodiclexic_condition import ConditionComparisonService
from at_tutoring_skills.core.task.service import TaskService


class SkillsTestCase(TestCase):
    def setUp(self):
        ImportKbCommand().handle()
        self.task_service = TaskService()
        self.user, _ = async_to_sync(self.task_service.create_user)("default")

    def test_descriptions(self):
        text = async_to_sync(self.task_service.get_variant_tasks_description)(self.user, skip_completed=False)
        print(text)

    def test_conditions(self):
        service = ConditionComparisonService()

        text = json.loads(
            """
            {
                    "tag": "rule",
                    "id": "Смена_статуса_средняя_низкая_ЛПУ2_Х",
                    "condition": {
                        "tag": "or",
                        "left": {
                            "tag": "and",
                            "left": {
                                "tag": "gt",
                                "left": {
                                    "tag": "sub",
                                    "left": {
                                        "tag": "ref",
                                        "id": "Счетчик_ЛПУ2",
                                        "ref": {
                                            "tag": "ref",
                                            "id": "Х_0_запроса_назад",
                                            "ref": null,
                                            "non_factor": {
                                                "tag": "with",
                                                "belief": 50,
                                                "probability": 100,
                                                "accuracy": 0
                                            }
                                        },
                                        "non_factor": {
                                            "tag": "with",
                                            "belief": 50,
                                            "probability": 100,
                                            "accuracy": 0
                                        }
                                    },
                                    "right": {
                                        "tag": "ref",
                                        "id": "Счетчик_ЛПУ2",
                                        "ref": {
                                            "tag": "ref",
                                            "id": "Х_2_запроса_назад",
                                            "ref": null,
                                            "non_factor": {
                                                "tag": "with",
                                                "belief": 50,
                                                "probability": 100,
                                                "accuracy": 0
                                            }
                                        },
                                        "non_factor": {
                                            "tag": "with",
                                            "belief": 50,
                                            "probability": 100,
                                            "accuracy": 0
                                        }
                                    },
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 50,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "right": {
                                    "tag": "value",
                                    "content": 60,
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 100,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            },
                            "right": {
                                "tag": "eq",
                                "left": {
                                    "tag": "ref",
                                    "id": "ЛПУ_2",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "Загруженность_хирургии",
                                        "ref": null,
                                        "non_factor": {
                                            "tag": "with",
                                            "belief": 50,
                                            "probability": 100,
                                            "accuracy": 0
                                        }
                                    },
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 50,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "right": {
                                    "tag": "value",
                                    "content": "средняя",
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 50,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            },
                            "non_factor": {
                                "tag": "with",
                                "belief": 50,
                                "probability": 100,
                                "accuracy": 0
                            }
                        },
                        "right": {
                            "tag": "gt",
                            "left": {
                                "tag": "ref",
                                "id": "ЛПУ_2",
                                "ref": {
                                    "tag": "ref",
                                    "id": "Количество_мест_в_хирургии",
                                    "ref": null,
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 50,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            },
                            "right": {
                                "tag": "value",
                                "content": 30,
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            },
                            "non_factor": {
                                "tag": "with",
                                "belief": 50,
                                "probability": 100,
                                "accuracy": 0
                            }
                        },
                        "non_factor": {
                            "tag": "with",
                            "belief": 50,
                            "probability": 100,
                            "accuracy": 0
                        }
                    },
                    "instructions": [
                        {
                            "tag": "assign",
                            "non_factor": {
                                "tag": "with",
                                "belief": 50,
                                "probability": 100,
                                "accuracy": 0
                            },
                            "ref": {
                                "tag": "ref",
                                "id": "ЛПУ_2",
                                "ref": {
                                    "tag": "ref",
                                    "id": "Загруженность_хирургии",
                                    "ref": null,
                                    "non_factor": {
                                        "tag": "with",
                                        "belief": 50,
                                        "probability": 100,
                                        "accuracy": 0
                                    }
                                },
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            },
                            "value": {
                                "tag": "value",
                                "content": "низкая",
                                "non_factor": {
                                    "tag": "with",
                                    "belief": 50,
                                    "probability": 100,
                                    "accuracy": 0
                                }
                            }
                        }
                    ],
                    "else_instructions": null,
                    "meta": "simple",
                    "period": null,
                    "desc": "Смена_статуса_средняя_низкая_ЛПУ2_Х"
                }
                """
        )
        context = ATKRLContext(name="1")
        d = text
        kb_rule = KBRuleModel(**d)
        kb_rule1 = kb_rule.to_internal(context)

        array = service.get_various_references(
            condition=kb_rule1.condition,
            max_depth=5,
        )
        kb_rule1.condition = array[0]

        print(kb_rule1.krl)
        kb_rule1.condition = array[1]

        print(kb_rule1.krl)

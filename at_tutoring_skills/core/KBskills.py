from asgiref.sync import sync_to_async
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from rest_framework import exceptions

from at_tutoring_skills.apps.skills.models import SUBJECT_CHOICES
from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.core.errors.models import CommonMistake
from at_tutoring_skills.core.knowledge_base.event.service import KBEventService
from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService
from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService
from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService
from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.task.skill_service import SkillService
from at_tutoring_skills.core.task.transitions import TransitionsService


class ATTutoringKBSkills(ATComponent):
    skills: dict = None
    cash: dict = None
    task_service: TaskService
    type_service: KBTypeService
    object_service: KBObjectService
    event_service: KBEventService
    interval_service: KBIntervalService
    rule_service: KBRuleService
    transition_service: TransitionsService

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.skills = {}  # временное хранилище, тут лучше подключить БД или что-то
        self.task_service = TaskService()
        self.type_service = KBTypeService()
        self.object_service = KBObjectService(self)
        self.event_service = KBEventService()
        self.interval_service = KBIntervalService()
        self.rule_service = KBRuleService()
        self.transition_service = TransitionsService()
        self.skill_service = SkillService()

    async def get_user_id_or_token(self, auth_token: str) -> int | str:
        if await self.check_external_registered("AuthWorker"):
            user_id = await self.exec_external_method(
                reciever="AuthWorker",
                methode_name="verify_token",
                method_args={"token": auth_token},
            )
            # await User.objects.aget_or_create(user_id=user_id, variant=Variant.objects.filter(name="1"))
            return user_id
        return auth_token

    # =================================== kb ========================================

    @authorized_method
    async def handle_knowledge_base_created(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, _ = await self.task_service.create_user(user_id)
        msg = await self.task_service.get_variant_tasks_description(
            user, skip_completed=False, task_object=SUBJECT_CHOICES.KB_TYPE
        )

        if event == "knowledgeBase/update":
            return {"msg": msg, "hint": msg, "kb_id": data["result"]["id"]}
        if event == "knowledgeBase/create":
            return {"msg": msg, "hint": msg, "kb_id": data["result"]["knowledgeBase"]["id"]}

    @authorized_method
    async def handle_knowledge_base_updated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, _ = await self.task_service.create_user(user_id)
        msg = await self.task_service.get_variant_tasks_description(
            user, skip_completed=False, task_object=SUBJECT_CHOICES.KB_TYPE
        )
        return {"msg": msg, "hint": msg, "kb_id": data["result"]["id"]}

    # ============================= type ===================

    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str) -> None:
        pass

    async def print_all_tasks_async(self):
        @sync_to_async
        def get_all_tasks():
            return list(TaskUser.objects.all())

        tasks = await get_all_tasks()
        for task in tasks:
            print(f"\n ID: {task.pk}\n")

    async def get_errors_result(self, errors_list, user, task, task_object):
        serialized_errors = [error.model_dump() for error in errors_list]
        errors_message = " ".join(
            [f"Ошибка №{i+1}: {error.get('tip', 'Неизвестная ошибка')}" for i, error in enumerate(serialized_errors)]
        )

        skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)

        tasks = await self.task_service.get_variant_tasks_description(
            user, skip_completed=False, task_object=task_object
        )

        return {
            "status": "error",
            "message": f"Обнаружены ошибки: {errors_message}",
            "stage_done": False,
            "url": errors_message,
            "hint": tasks,
            "skills": skills,
        }

    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_TYPE
        errors_list = []

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

        task: Task = await self.task_service.get_task_by_name(kb_type.id, task_object)

        if task:
            et_type = await self.task_service.get_type_reference(task)

            errors_list = await self.type_service.handle_logic_lexic_mistakes(user, task, kb_type, et_type)
            if errors_list:
                return await self.get_errors_result(errors_list, user, task, task_object)
            else:
                
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 1)

                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object=SUBJECT_CHOICES.KB_OBJECT
               
                tasks = await self.task_service.get_variant_tasks_description(
                    user, skip_completed=False, task_object=task_object
                )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
                
                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    "hint": tasks,
                    "skills": skills,
                }
        else:
            tasks = await self.task_service.get_variant_tasks_description(
                user, skip_completed=False, task_object=task_object
            )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False, "hint": tasks}

    @authorized_method
    async def handle_kb_type_duplicated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_TYPE
        errors_list = []
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        try:
            kb_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

    @authorized_method
    async def handle_kb_type_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        type_dict_raw = data.get("result")

    # ==================================object ===========================================

    @authorized_method
    async def handle_kb_object_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_object_duplicated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_OBJECT
        errors_list = []
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        try:
            kb_object = await self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_OBJECT
        errors_list = []

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_object = await self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

        task: Task = await self.task_service.get_task_by_name(kb_object.id, 2)

        if task:
            obj_et = await self.task_service.get_object_reference(task)
            errors_list = await self.object_service.handle_logic_lexic_mistakes(user, task, kb_object, obj_et)
            if errors_list:
                return await self.get_errors_result(errors_list, user, task, task_object)
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 2)

                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object=SUBJECT_CHOICES.KB_EVENT
               
                tasks = await self.task_service.get_variant_tasks_description(
                    user, skip_completed=False, task_object=task_object
                )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
                
                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    "hint": tasks,
                    "skills": skills,
                }
        else:
            tasks = await self.task_service.get_variant_tasks_description(
                user, skip_completed=False, task_object=task_object
            )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {"msg": "обучаемый успешно выполнил задание", "hint": tasks, "skills": skills}

    @authorized_method
    async def handle_kb_object_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)

        object_dict_raw = data.get("result")

    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_EVENT
        errors_list = []

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_event = await self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )
        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

        task: Task = await self.task_service.get_task_by_name(kb_event.id, 3)

        if task:
            event_et = await self.task_service.get_event_reference(task)

            errors_list = await self.event_service.handle_logic_lexic_mistakes(user, task, kb_event, event_et)
            if errors_list:
                return await self.get_errors_result(errors_list, user, task, task_object)
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 3)
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object=SUBJECT_CHOICES.KB_INTERVAL
               
                tasks = await self.task_service.get_variant_tasks_description(
                    user, skip_completed=False, task_object=task_object
                )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
                
                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    "hint": tasks,
                    "skills": skills,
                }
        else:
            tasks = await self.task_service.get_variant_tasks_description(
                user, skip_completed=False, task_object=task_object
            )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                "hint": tasks,
                "skills": skills,
            }

    @authorized_method
    async def handle_kb_event_duplicated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_EVENT
        errors_list = []
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        try:
            kb_event = await self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

    @authorized_method
    async def handle_kb_event_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        event_dict_raw = data.get("result")

    # ==================================interval==================================

    @authorized_method
    async def handle_kb_interval_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_interval_updated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_INTERVAL
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_interval = await self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Interval Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_interval.id, 4)

        if task:
            interval_et = await self.task_service.get_interval_reference(task)
            errors_list = await self.interval_service.handle_logic_lexic_mistakes(user, task, kb_interval, interval_et)
            if errors_list:
                return await self.get_errors_result(errors_list, user, task, task_object)
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 4)
                
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)
                    task_object=SUBJECT_CHOICES.KB_RULE
               
                tasks = await self.task_service.get_variant_tasks_description(
                    user, skip_completed=False, task_object=task_object
                )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
                
                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    "hint": tasks,
                    "skills": skills,
                }
        else:
            tasks = await self.task_service.get_variant_tasks_description(
                user, skip_completed=False, task_object=task_object
            )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                "hint": tasks,
                "skills": skills,
            }

    @authorized_method
    async def handle_kb_interval_duplicated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_INTERVAL
        errors_list = []
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        try:
            kb_interval = await self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

    @authorized_method
    async def handle_kb_interval_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)

        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        interval_raw = data.get("result")

    # ====================================RULE============================
    @authorized_method
    async def handle_kb_rule_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_rule_updated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_RULE
        errors_list = []

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_rule = await self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )
        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

        task: Task = await self.task_service.get_task_by_name(kb_rule.id, 5)

        if task:
            rule_et = await self.task_service.get_rule_reference(task)
            errors_list = await self.rule_service.handle_logic_lexic_mistakes(user, task, kb_rule, rule_et)
            if errors_list:
                return await self.get_errors_result(errors_list, user, task, task_object)
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, task_object=task_object)  
                kb = ""
                
                if stage:
                    await self.skill_service.complete_skills_stage_done(user, task_object=task_object)   
                    task_object = None
                    knowledge_base = data['result']['knowledge_base']
                    kb = await self.exec_external_method(
                        'ATKRLEditor',
                        'get_knowledge_base',
                        {
                            'id': knowledge_base,
                            'format': 'at_krl'
                        },
                        auth_token=auth_token
                    )

                tasks = await self.task_service.get_variant_tasks_description(
                    user, skip_completed=False, task_object=task_object
                )
                skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
                return {
                    "msg": "обучаемый успешно выполнил задание",
                    "stage_done": stage,
                    "hint": tasks,
                    "skills": skills,
                    "kb": kb,
                }
        else:
            tasks = await self.task_service.get_variant_tasks_description(
                user, skip_completed=False, task_object=task_object
            )
            skills = await self.skill_service.process_and_get_skills_string(user, task_object=task_object)
            return {
                "msg": "Задание не найдено,  продолжайте выполнение работы",
                "stage_done": False,
                "hint": tasks,
                "skills": skills,
            }

    @authorized_method
    async def handle_kb_rule_duplicated(self, event: str, data: dict, auth_token: str):
        task_object = SUBJECT_CHOICES.KB_RULE
        errors_list = []
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_rule = await self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            errors_list.append(
                CommonMistake(
                    user_id=user_id,
                    type="syntax",
                    task_id=None,
                    fine=1,
                    coefficient=0,
                    tip=str(e.detail),
                    is_tip_shown=False,
                    skills=[],
                )
            )

        if errors_list:
            return await self.get_errors_result(errors_list, user, None, task_object)

    @authorized_method
    async def handle_kb_rule_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)

        await self.task_service.create_task_user_entries(user)

        rule_dict_raw = data.get("result")

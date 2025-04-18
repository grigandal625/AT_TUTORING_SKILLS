from urllib.parse import quote_plus

from asgiref.sync import sync_to_async
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from rest_framework import exceptions

from at_tutoring_skills.apps.skills.models import Task
from at_tutoring_skills.apps.skills.models import TaskUser
from at_tutoring_skills.core.knowledge_base.event.service import KBEventService
from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService
from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService
from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService
from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService
from at_tutoring_skills.core.task.service import TaskService
from at_tutoring_skills.core.task.transitions import TransitionsService


class ATTutoringKBSkills(ATComponent):
    skills: dict = None
    cash: dict = None
    task_service = None
    type_service = None
    object_service = None
    event_service = None
    interval_service = None
    rule_service = None
    transition_service = None

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.skills = {}  # временное хранилище, тут лучше подключить БД или что-то
        self.cash = {}
        self.task_service = TaskService()
        self.type_service = KBTypeService()
        self.object_service = KBObjectService(self)
        self.event_service = KBEventService()
        self.interval_service = KBIntervalService()
        self.rule_service = KBRuleService()
        self.transition_service = TransitionsService()

    def init_cash(self, auth_token_or_id: str):
        if auth_token_or_id not in self.cash:
            self.cash[auth_token_or_id] = {}
        if "kb_types" not in self.cash[auth_token_or_id]:
            self.cash[auth_token_or_id]["kb_types"] = []
        if "kb_objects" not in self.cash[auth_token_or_id]:
            self.cash[auth_token_or_id]["kb_objects"] = []
        if "kb_events" not in self.cash[auth_token_or_id]:
            self.cash[auth_token_or_id]["kb_events"] = []
        if "kb_intervals" not in self.cash[auth_token_or_id]:
            self.cash[auth_token_or_id]["kb_intervals"] = []
        if "kb_rules" not in self.cash[auth_token_or_id]:
            self.cash[auth_token_or_id]["kb_rules"] = []
        return self.cash[auth_token_or_id]

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

    # =================================== det value from element by key ===========================

    def get_obj_id_by_kbid(self, kb_id: str, array_name: str, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)

        res_item = None
        if array_name in cash:
            for item in cash[array_name]:
                if item.kb_id == kb_id:
                    res_name = item.id
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению kb_id",
                kb_id,
                " ничего не найдено",
            )
        return res_name

    def get_obj_kbid_by_id(self, id: str, array_name: str, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)
        res_item = None
        if array_name in cash:
            for item in cash[array_name]:
                if item.id == id:
                    res_name = item.kb_id
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению id",
                id,
                " ничего не найдено",
            )
        return res_name

    def get_obj_by_id(self, array_name: str, key_value: str, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)
        res_item = None
        if array_name in cash:
            for item in cash[array_name]:
                if item.id == key_value:
                    res_item = item
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению имени",
                key_value,
                " ничего не найдено",
            )
        return res_item

    def get_obj_by_kbid(self, array_name: str, key_value: int, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)
        res_item = None
        if array_name in cash:
            for item in cash[array_name]:
                if item.kb_id == key_value:
                    res_item = item
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению имени",
                key_value,
                " ничего не найдено",
            )
        return res_item

    def get_obj_arrayid_by_id(self, id: str, array_name: str, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)

        res = None
        if array_name in cash:
            for i in range(len(cash[array_name])):
                if cash[array_name][i].id == id:
                    res = i
        if res is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению kb_id",
                id,
                " ничего не найдено",
            )
        return res

    def calc_elements(self, array_name, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return len(self.cash[auth_token_or_id][array_name])

    def calc_kb_types(self, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return self.calc_elements("kb_types", auth_token_or_id)

    def calc_kb_objects(self, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return self.calc_elements("kb_objects", auth_token_or_id)

    def calc_kb_events(self, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return self.calc_elements("kb_events", auth_token_or_id)

    def calc_kb_intervals(self, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return self.calc_elements("kb_intervals", auth_token_or_id)

    def calc_kb_rules(self, auth_token_or_id: str):
        self.init_cash(auth_token_or_id)
        return self.calc_elements("kb_rules", auth_token_or_id)

    # ============================== add to cash ====================================
    def add_to_cash(self, array_name: str, data, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)
        arrayid = self.get_obj_arrayid_by_id(data.id, array_name, auth_token_or_id)
        if arrayid is not None:
            cash[array_name][arrayid] = data
        else:
            cash[array_name].append(data)
        self.cash[auth_token_or_id] = cash

    def add_type_to_cash(self, data, auth_token_or_id):
        self.add_to_cash("kb_types", data, auth_token_or_id)

    def add_object_to_cash(self, data, auth_token_or_id):
        self.add_to_cash("kb_objects", data, auth_token_or_id)

    def add_event_to_cash(self, data, auth_token_or_id):
        self.add_to_cash("kb_events", data, auth_token_or_id)

    def add_interval_to_cash(self, data, auth_token_or_id):
        self.add_to_cash("kb_intervals", data, auth_token_or_id)

    def add_rule_to_cash(self, data, auth_token_or_id):
        self.add_to_cash("kb_rules", data, auth_token_or_id)

    # =============================== delete from kash ==============================

    def remove_from_cash(self, id, array_name: str, auth_token_or_id: str):
        cash = self.init_cash(auth_token_or_id)
        arrayid = self.get_obj_arrayid_by_id(id, array_name, auth_token_or_id)
        if arrayid is not None:
            del cash[array_name][arrayid]
        else:
            print("Объект не найден")
        self.cash[auth_token_or_id] = cash

    def remove_type_from_cash(self, id, auth_token_or_id: str):
        self.remove_from_cash(id, "kb_types", auth_token_or_id)

    def remove_object_from_cash(self, id, auth_token_or_id: str):
        self.remove_from_cash(id, "kb_objects", auth_token_or_id)

    def remove_event_from_cash(self, id, auth_token_or_id: str):
        self.remove_from_cash(id, "kb_events", auth_token_or_id)

    def remove_interval_from_cash(self, id, auth_token_or_id: str):
        self.remove_from_cash(id, "kb_intervals", auth_token_or_id)

    def remove_rule_from_cash(self, id, auth_token_or_id: str):
        self.remove_from_cash(id, "kb_rules", auth_token_or_id)

    # =================================== kb ========================================

    @authorized_method
    async def handle_knowledge_base_created(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        msg = await self.task_service.get_variant_tasks_description(user, scip_completed=True)

        return {"msg": msg, "hint": msg, "kb_id": data["result"]["knowledgeBase"]["id"]}

    @authorized_method
    async def handle_knowledge_base_updated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        self.init_cash(user_id)

    @authorized_method
    async def handle_kb_types_get(self, event: str, data: dict, auth_token: str):
        # user_id = self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)
        # types_array = data["result"]["items"]

        # for item in types_array:
        #     self.add_type_to_cash("kb_types", auth_token)
        ...

    @authorized_method
    async def handle_kb_objects_get(self, event: str, data: dict, auth_token: str):
        # user_id = self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)
        # types_array = data["result"]["items"]

        # for item in types_array:
        #     self.add_type_to_cash("kb_objects", auth_token)
        ...

    @authorized_method
    async def handle_kb_events_get(self, event: str, data: dict, auth_token: str):
        # user_id = self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)
        # types_array = data["result"]["items"]

        # for item in types_array:
        #     self.add_type_to_cash("kb_events", auth_token)
        ...

    @authorized_method
    async def handle_kb_intervals_get(self, event: str, data: dict, auth_token: str):
        # user_id = self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)
        # types_array = data["result"]["items"]

        # for item in types_array:
        #     self.add_type_to_cash("kb_intervals", auth_token)
        ...

    @authorized_method
    async def handle_kb_rules_get(self, event: str, data: dict, auth_token: str):
        # user_id = self.get_user_id_or_token(auth_token)
        # self.init_cash(user_id)
        # types_array = data["result"]["items"]

        # for item in types_array:
        #     self.add_type_to_cash("kb_rules", auth_token)
        ...

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

    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал тип (БЗ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        user, created = await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_type.id, 1)

        if task:
            et_type = await self.task_service.get_type_reference(task)
            print(et_type)
            errors_list = None
            errors_list = await self.type_service.handle_logic_lexic_mistakes(user, task, kb_type, et_type)
            if errors_list:
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                encoded_text = quote_plus(errors_message)

                return {
                    "status": "error",
                    "message": f"Обнаружены ошибки: {errors_message}",
                    "stage_done": False,
                    "url": errors_message,
                }
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 1)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
        else:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

    @authorized_method
    async def handle_kb_type_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал тип (БЗ): ", data)
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_type.id, 1)
        print(task.object_name, task.object_reference)
        type_et = await self.task_service.get_type_reference(task)
        print(type_et)

        # self.add_type_to_cash(kb_type, user_id)

    @authorized_method
    async def handle_kb_type_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        type_dict_raw = data.get("result")
        type_id = type_dict_raw.get("itemId")

        self.remove_type_from_cash(type_id, user_id)

    # ==================================object ===========================================

    @authorized_method
    async def handle_kb_object_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_object_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_object = await self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_object.id, 2)
        print(task.object_name, task.object_reference)
        obj_type = await self.task_service.get_object_reference(task)
        print(obj_type)

        # self.add_object_to_cash(kb_object, user_id)

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал объект (БЗ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_object = await self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Object Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_object.id, 2)
        # await self.task_service.create_task_user_safe(task, user)

        obj_et = await self.task_service.get_object_reference(task)
        print(obj_et)

        if task:
            errors_list = None
            errors_list = await self.object_service.handle_logic_lexic_mistakes(user, task, kb_object, obj_et)
            if errors_list:
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                encoded_text = quote_plus(errors_message)

                return {
                    "status": "error",
                    "message": f"Обнаружены ошибки: {errors_message}",
                    "stage_done": False,
                    "url": errors_message,
                }
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 2)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
        else:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

    @authorized_method
    async def handle_kb_object_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        object_dict_raw = data.get("result")
        object_id = object_dict_raw.get("itemId")

        self.remove_object_from_cash(object_id, user_id)

    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал событие (БЗ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        user_id = user.pk

        try:
            kb_event = await self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Event Created: Syntax Mistakes: {e}") from e
        print(kb_event.id)
        task: Task = await self.task_service.get_task_by_name(kb_event.id, 3)

        if task:
            # await self.task_service.create_task_user_safe(task, user)

            event_et = await self.task_service.get_event_reference(task)
            print(event_et)

            # self.add_event_to_cache(kb_event, user_id)
            errors_list = await self.event_service.handle_logic_lexic_mistakes(user, task, kb_event, event_et)
            if errors_list:
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                encoded_text = quote_plus(errors_message)

                return {
                    "status": "error",
                    "message": f"Обнаружены ошибки: {errors_message}",
                    "stage_done": False,
                    "url": errors_message,
                }
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 3)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
        else:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

    @authorized_method
    async def handle_kb_event_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_event = await self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        # self.add_event_to_cash(kb_event, user_id)

    @authorized_method
    async def handle_kb_event_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        event_dict_raw = data.get("result")
        event_id = event_dict_raw.get("itemId")

        self.remove_event_from_cash(event_id, user_id)

    # ==================================interval==================================

    @authorized_method
    async def handle_kb_interval_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_interval_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал интервал (БЗ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_interval = await self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Interval Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_interval.id, 4)
        if task:
            # await self.task_service.create_task_user_safe(task, user)

            interval_et = await self.task_service.get_interval_reference(task)
            print(interval_et)
            errors_list = None
            errors_list = await self.interval_service.handle_logic_lexic_mistakes(user, task, kb_interval, interval_et)
            if errors_list:
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                encoded_text = quote_plus(errors_message)

                return {
                    "status": "error",
                    "message": f"Обнаружены ошибки: {errors_message}",
                    "stage_done": False,
                    "url": errors_message,
                }
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 4)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
        else:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

    @authorized_method
    async def handle_kb_interval_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_interval = await self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        # self.add_interval_to_cash(kb_interval, user_id)

    @authorized_method
    async def handle_kb_interval_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)

        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        interval_raw = data.get("result")
        interval_id = interval_raw.get("itemId")

        self.remove_interval_from_cash(interval_id, user_id)

    # ====================================RULE============================
    @authorized_method
    async def handle_kb_rule_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_rule_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал правило (БЗ): ", data)

        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)
        user_id = user.pk

        try:
            kb_rule = await self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Rule Created: Syntax Mistakes: {e}") from e

        task: Task = await self.task_service.get_task_by_name(kb_rule.id, 5)
        # await self.task_service.create_task_user_safe(task, user)

        rule_et = await self.task_service.get_rule_reference(task)
        print(rule_et)

        if task:
            errors_list = None
            errors_list = await self.rule_service.handle_logic_lexic_mistakes(user, task, kb_rule, rule_et)
            if errors_list:
                serialized_errors = [error.model_dump() for error in errors_list]
                errors_message = " ".join(
                    f"Ошибка: {error.get('tip', 'Неизвестная ошибка')}" for error in serialized_errors
                )
                encoded_text = quote_plus(errors_message)

                return {
                    "status": "error",
                    "message": f"Обнаружены ошибки: {errors_message}",
                    "stage_done": False,
                    "url": errors_message,
                }
            else:
                await self.task_service.complete_task(task, user)
                stage = await self.transition_service.check_stage_tasks_completed(user, 5)
                return {"msg": "обучаемый успешно выполнил задание", "stage_done": stage}
        else:
            return {"msg": "Задание не найдено,  продолжайте выполнение работы", "stage_done": False}

    @authorized_method
    async def handle_kb_rule_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        try:
            kb_rule = await self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        # self.add_rule_to_cash(kb_rule, user_id)

    @authorized_method
    async def handle_kb_rule_deleted(self, event: str, data: dict, auth_token: str):
        user_id = await self.get_user_id_or_token(auth_token)
        user, created = await self.task_service.create_user(user_id)
        await self.task_service.create_user_skill_connection(user)
        await self.task_service.asign_user_random_variant(user)
        await self.task_service.create_task_user_entries(user)

        rule_dict_raw = data.get("result")
        rule_id = rule_dict_raw.get("itemId")

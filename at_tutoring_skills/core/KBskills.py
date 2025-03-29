from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from rest_framework import exceptions

from at_tutoring_skills.core.knowledge_base.event.service import KBEventService
from at_tutoring_skills.core.knowledge_base.interval.service import KBIntervalService
from at_tutoring_skills.core.knowledge_base.object.service import KBObjectService
from at_tutoring_skills.core.knowledge_base.rule.service import KBRuleService
from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService
from at_tutoring_skills.core.task.service import Repository
from at_tutoring_skills.core.task.service import TaskService


class ATTutoringKBSkills(ATComponent):
    skills: dict = None
    cash: dict = None
    repository = None
    type_service = None
    object_service = None
    event_service = None
    interval_service = None
    rule_service = None

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.repository = Repository
        self.skills = {}  # временное хранилище, тут лучше подключить БД или что-то
        self.cash = {}
        self.type_service = KBTypeService(self.repository)
        self.object_service = KBObjectService(self.repository)
        self.event_service = KBEventService(self.repository)
        self.interval_service = KBIntervalService(self.repository)
        self.rule_service = KBRuleService(self.repository)

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
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)

    @authorized_method
    async def handle_knowledge_base_updated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)

    @authorized_method
    async def handle_kb_types_get(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)
        types_array = data["result"]["items"]

        for item in types_array:
            self.add_type_to_cash("kb_types", auth_token)

    @authorized_method
    async def handle_kb_objects_get(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)
        types_array = data["result"]["items"]

        for item in types_array:
            self.add_type_to_cash("kb_objects", auth_token)

    @authorized_method
    async def handle_kb_events_get(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)
        types_array = data["result"]["items"]

        for item in types_array:
            self.add_type_to_cash("kb_events", auth_token)

    @authorized_method
    async def handle_kb_intervals_get(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)
        types_array = data["result"]["items"]

        for item in types_array:
            self.add_type_to_cash("kb_intervals", auth_token)

    @authorized_method
    async def handle_kb_rules_get(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        self.init_cash(user_id)
        types_array = data["result"]["items"]

        for item in types_array:
            self.add_type_to_cash("kb_rules", auth_token)

    # ============================= type ===================

    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str) -> None:
        pass

    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал тип (БЗ): ", data)
        user_id = self.get_user_id_or_token(auth_token)

        try:
            kb_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        # заглушка
        et_type = await self.type_service.handle_syntax_mistakes(user_id, data)
        et_type.values[0] = "D"

        try:
            self.type_service.handle_logic_lexic_mistakes(user_id, kb_type, et_type)
        except ExceptionGroup as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_type.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_type_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)
        try:
            kb_type = self.type_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_type_to_cash(kb_type, user_id)

    @authorized_method
    async def handle_kb_type_deleted(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        type_dict_raw = data.get("result")
        type_id = type_dict_raw.get("itemId")

        self.remove_type_from_cash(type_id, user_id)

    # ==================================object ===========================================

    @authorized_method
    async def handle_kb_object_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_object_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_object = self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_object_to_cash(kb_object, user_id)

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_object = self.object_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_object_to_cash(kb_object, user_id)

        try:
            self.object_service.handle_logic_lexic_mistakes(user_id, kb_object)
        except ExceptionGroup as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_object.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_object_deleted(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        object_dict_raw = data.get("result")
        object_id = object_dict_raw.get("itemId")

        self.remove_object_from_cash(object_id, user_id)

    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_event = self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_event_to_cash(kb_event, user_id)

        try:
            self.event_service.handle_logic_lexic_mistakes(user_id, kb_event)
        except ExceptionGroup as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_event.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_event_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_event = self.event_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_event_to_cash(kb_event, user_id)

    @authorized_method
    async def handle_kb_event_deleted(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        event_dict_raw = data.get("result")
        event_id = event_dict_raw.get("itemId")

        self.remove_event_from_cash(event_id, user_id)

    # ==================================interval==================================

    @authorized_method
    async def handle_kb_interval_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_interval_updated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_interval = self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_interval_to_cash(kb_interval, user_id)

        try:
            self.interval_service.handle_logic_lexic_mistakes(user_id, kb_interval)
        except ExceptionGroup as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_interval.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_interval_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_interval = self.interval_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_interval_to_cash(kb_interval, user_id)

    @authorized_method
    async def handle_kb_interval_deleted(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        interval_raw = data.get("result")
        interval_id = interval_raw.get("itemId")

        self.remove_interval_from_cash(interval_id, user_id)

    # ====================================RULE============================
    @authorized_method
    async def handle_kb_rule_created(self, event: str, data: dict, auth_token: str):
        pass

    @authorized_method
    async def handle_kb_rule_updated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_rule = self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_rule_to_cash(kb_rule, user_id)

        try:
            self.rule_service.handle_logic_lexic_mistakes(user_id, kb_rule)
        except ExceptionGroup as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_rule.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_rule_duplicated(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        try:
            kb_rule = self.rule_service.handle_syntax_mistakes(user_id, data)
        except exceptions.ValidationError as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        self.add_rule_to_cash(kb_rule, user_id)

    @authorized_method
    async def handle_kb_rule_deleted(self, event: str, data: dict, auth_token: str):
        user_id = self.get_user_id_or_token(self, auth_token)

        rule_dict_raw = data.get("result")
        rule_id = rule_dict_raw.get("itemId")

        self.remove_rule_from_cash(rule_id, user_id)

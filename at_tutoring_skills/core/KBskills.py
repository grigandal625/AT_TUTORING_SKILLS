from at_krl.core.kb_class import KBClass
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_type import KBType
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method

from at_tutoring_skills.core.knowledge_base.errors import Repository
from at_tutoring_skills.core.knowledge_base.type.service import KBTypeService
from at_tutoring_skills.core.task.service import TaskService

# from at_krl.core.kb_operation import KBOperation


class ATTutoringKBSkills(ATComponent):
    skills: dict = None
    cash: dict = None
    repository = None

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.repository = Repository
        self.skills = {}  # временное хранилище, тут лучше подключить БД или что-то
        self.cash = {}

    def init_cash(self, auth_token: str):
        if auth_token not in self.cash:
            self.cash[auth_token] = {}
        if "kb_types" not in self.cash[auth_token]:
            self.cash[auth_token]["kb_types"] = []
        if "kb_objects" not in self.cash[auth_token]:
            self.cash[auth_token]["kb_objects"] = []
        if "kb_events" not in self.cash[auth_token]:
            self.cash[auth_token]["kb_events"] = []
        if "kb_intervals" not in self.cash[auth_token]:
            self.cash[auth_token]["kb_intervals"] = []
        if "kb_rules" not in self.cash[auth_token]:
            self.cash[auth_token]["kb_rules"] = []
        return self.cash[auth_token]

    # =================================== det value from element by key ===========================

    def get_obj_id_by_kbid(self,
                               kb_id: str,
                               array_name: str,
                               auth_token: str
                               ):
        
        cash = self.init_cash(auth_token)

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

    def get_obj_kbid_by_id(self,
                            id: str,
                            array_name: str,
                            auth_token: str
                            ):
        
        cash = self.init_cash(auth_token)
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

    def get_obj_by_id(self,
                           array_name: str,
                           key_value: str,
                           auth_token: str
                           ):
        cash = self.init_cash(auth_token)
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
    
    def get_obj_by_kbid(self,
                        array_name: str,
                        key_value: int,
                        auth_token: str
                        ):
        cash = self.init_cash(auth_token)
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

    def get_obj_arrayid_by_id(self,
                               id: str,
                               array_name: str,
                               auth_token: str
                               ):
        
        cash = self.init_cash(auth_token)

        res_item = None
        if array_name in cash:
            for i in range(len(cash[array_name])):
                if cash[array_name][i].id == id:
                    res = i
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по значению kb_id",
                id,
                " ничего не найдено",
            )
        return res
    
    def calc_elements(self, array_name, auth_token: str):
        self.init_cash(auth_token)
        return len(self.cash[auth_token][array_name])

    def calc_kb_types(self, auth_token: str):
        self.init_cash(auth_token)
        return self.calc_elements("kb_types", auth_token)

    def calc_kb_objects(self, auth_token: str):
        self.init_cash(auth_token)
        return self.calc_elements("kb_objects", auth_token)

    def calc_kb_events(self, auth_token: str):
        self.init_cash(auth_token)
        return self.calc_elements("kb_events", auth_token)

    def calc_kb_intervals(self, auth_token: str):
        self.init_cash(auth_token)
        return self.calc_elements("kb_intervals", auth_token)

    def calc_kb_rules(self, auth_token: str):
        self.init_cash(auth_token)
        return self.calc_elements("kb_rules", auth_token)

    # ============================== add to cash ====================================
    def add_to_cash(self, array_name: str, data, auth_token: str):
        cash = self.init_cash(auth_token)
        arrayid = self.get_obj_arrayid_by_id(id = id, array_name = array_name, auth_token=auth_token) 
        if arrayid is not None:
            cash[array_name][arrayid] = data
        else:
            cash[array_name].append(data)
        self.cash[auth_token] = cash

    def add_type_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash("kb_types", "id", data, auth_token)

    def add_object_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash("kb_objects", "id", data, auth_token)

    def add_event_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash("kb_events", "Name", data, auth_token)

    def add_interval_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash("kb_intervals", "Name", data, auth_token)

    def add_rule_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash("kb_rules", "id", data, auth_token)

    # =============================== delete from kash ==============================

    def remove_from_cash(self, key_val, del_field, search_field: str, auth_token: str):
        cash = self.init_cash(auth_token)
        print("check", len(cash[del_field]))
        index = self.get_index_by_smth(del_field, search_field, key_val, auth_token)
        if id is not None:
            del cash[del_field][index]  # kb_types
            print("\n element removed", len(cash[del_field]))
        else:
            print("Объект не найден")
        self.cash[auth_token] = cash

    def remove_type_from_cash(self, key_val, auth_token: str):
        self.remove_from_cash(key_val, "kb_types", "typeId", auth_token)

    def remove_object_from_cash(self, key_val, auth_token: str):
        self.remove_from_cash(key_val, "kb_objects", "objectId", auth_token)

    def remove_event_from_cash(self, key_val, auth_token: str):
        self.remove_from_cash(key_val, "kb_events", "eventId", auth_token)

    def remove_interval_from_cash(self, key_val, auth_token: str):
        self.remove_from_cash(key_val, "kb_intervals", "intervalId", auth_token)

    def remove_rule_from_cash(self, key_val, auth_token: str):
        self.remove_from_cash(key_val, "kb_rules", "ruleId", auth_token)

    # =================================== kb ========================================

    @authorized_method
    async def handle_knowledge_base_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал пустой тип (БЗ): ", data)
        self.init_cash(auth_token)

    @authorized_method
    async def handle_knowledge_base_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал пустой тип (БЗ): ", data)

        self.init_cash(auth_token)

    @authorized_method
    async def handle_kb_types_get(self, event: str, data: dict, auth_token: str):
        print("извлечение списка типов ", data)
        types_array = data["result"]["items"]
        print(types_array)
        for item in types_array:
            type_dict = self.kb_type_from_dict(item, event)
            self.add_type_to_cash(type_dict, auth_token)
            type_dict = {}

    @authorized_method
    async def handle_kb_objects_get(self, event: str, data: dict, auth_token: str):
        print("извлечение списка типов ", data)
        objects_array = data["result"]["items"]
        print(objects_array)
        for item in objects_array:
            object_dict = self.kb_object_from_dict(item, event, auth_token)
            self.add_object_to_cash(object_dict, auth_token)
            object_dict = {}

    @authorized_method
    async def handle_kb_events_get(self, event: str, data: dict, auth_token: str):
        print("извлечение списка событий ", data)
        events_array = data["result"]["items"]
        for item in events_array:
            event_dict = self.kb_event_from_dict(item, event)
            self.add_event_to_cash(event_dict, auth_token)
            event_dict = {}

    @authorized_method
    async def handle_kb_intervals_get(self, event: str, data: dict, auth_token: str):
        print("извлечение списка интервалов ", data)
        intervals_array = data["result"]["items"]
        for item in intervals_array:
            interval_dict = self.kb_interval_from_dict(item, event)
            self.add_interval_to_cash(interval_dict, auth_token)
            interval_dict = {}

    @authorized_method
    async def handle_kb_rules_get(self, event: str, data: dict, auth_token: str):
        print("извлечение списка правил ", data)
        rules_array = data["result"]["items"]
        for item in rules_array:
            rule_dict = self.kb_rule_from_dict(item, event)
            self.add_rule_to_cash(rule_dict, auth_token)
            rule_dict = {}

    # ============================= type ===================

    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал пустой тип (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        type_dict_raw = data.get("result")
        type_dict = self.kb_type_from_dict(type_dict_raw, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.add_type_to_cash(type_dict, auth_token)

        self.cash["kb_types"].append(type_dict)  # запись в кэш

        # current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)

        # self.skills[auth_token] = current_skills

        # if current_skills['kb_types'] >= 50:
        #     return {'skills': current_skills, 'stage_done': True}

        # return {'skills': current_skills, 'stage_done': False}

    @authorized_method
    async def handle_kb_type_created_1(self, event: str, data: dict, auth_token: str) -> None:
        user_id = self.AT_USER.parse_auth_token(auth_token)

        try:
            kb_type = KBTypeService.handle_syntax_mistakes(user_id, data)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Syntax Mistakes: {e}") from e

        try:
            KBTypeService.handle_logic_mistakes(user_id, kb_type)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Logic Mistakes: {e}") from e

        # try:
        #     KBTypeService.handle_lexic_mistakes(user_id, kb_type)
        # except BaseException as e:
        #     raise ValueError(f"Handle KB Type Created: Lexic Mistakes: {e}") from e

        try:
            TaskService.complete_task(user_id, event, kb_type.id)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Complete Task: {e}") from e

    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал тип (БЗ): ", data)

        # skill = await Skill.objects.acreate(name='test', scenario_name='test')
        # print(skill.name)

        current_skills = self.skills.get(auth_token, {})
        type_dict_raw = data.get("result")
        type_dict = self.kb_type_from_dict(type_dict_raw, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.add_type_to_cash(type_dict, auth_token)

        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Выполнены не все задания",
        }

    @authorized_method
    async def handle_kb_type_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый дублировал тип (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})
        type_dict_raw = data.get("result")
        type_dict_raw = type_dict_raw.get("item")
        type_dict = self.kb_type_from_dict(type_dict_raw, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.add_type_to_cash(type_dict, auth_token)

        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_type_deleted(self, event: str, data: dict, auth_token: str):
        print("Обучаемый удалил тип (БЗ): ", data)

        type_dict_raw = data.get("result")
        type_id = type_dict_raw.get("itemId")

        self.remove_type_from_cash(type_id, auth_token)

    # ==================================object ===========================================

    @authorized_method
    async def handle_kb_object_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал объект (БЗ): ", data)

        print(data)
        object_dict_raw = data.get("result")
        object_dict = self.kb_object_from_dict(object_dict_raw, event, auth_token)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)
        object_dict["model"] = kb_object
        self.add_object_to_cash(object_dict, auth_token)

    @authorized_method
    async def handle_kb_object_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый дублировал объект (БЗ): ", data)
        current_skills = self.skills.get(auth_token, {})
        object_dict_raw = data.get("result")
        object_dict_raw = object_dict_raw.get("item")
        object_dict = self.kb_object_from_dict(object_dict_raw, event, auth_token)

        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)
        object_dict["model"] = kb_object
        self.add_object_to_cash(object_dict, auth_token)

        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал объект (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})
        object_dict_raw = data.get("result")
        object_dict = self.kb_object_from_dict(object_dict_raw, event, auth_token)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)
        object_dict["model"] = kb_object
        self.add_object_to_cash(object_dict, auth_token)

    @authorized_method
    async def handle_kb_object_deleted(self, event: str, data: dict, auth_token: str):
        print("Обучаемый удалил объект (БЗ): ", data)

        object_dict_raw = data.get("result")
        object_id = object_dict_raw.get("itemId")

        self.remove_object_from_cash(object_id, auth_token)

    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал событие (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        print(data)
        event_dict_raw = data.get("result")
        event_dict = self.kb_event_from_dict(event_dict_raw, event)
        kb_event = KBEvent.from_dict(event_dict)
        print(kb_event.krl)
        event_dict["model"] = kb_event
        self.add_event_to_cash(event_dict, auth_token)

    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал событие (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        event_dict_raw = data.get("result")
        event_dict = self.kb_event_from_dict(event_dict_raw, event)
        kb_event = KBEvent.from_dict(event_dict)
        print(kb_event.krl)
        event_dict["model"] = kb_event
        self.add_event_to_cash(event_dict, auth_token)

    @authorized_method
    async def handle_kb_event_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый дублировал событие (БЗ): ", data)
        current_skills = self.skills.get(auth_token, {})
        event_dict_raw = data.get("result")
        event_dict_raw = event_dict_raw.get("item")
        event_dict = self.kb_event_from_dict(event_dict_raw, event)
        kb_event = KBEvent.from_dict(event_dict)
        print(kb_event.krl)
        event_dict["model"] = kb_event
        self.add_event_to_cash(event_dict, auth_token)
        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_event_deleted(self, event: str, data: dict, auth_token: str):
        print("Обучаемый удалил событие (БЗ): ", data)

        event_dict_raw = data.get("result")
        event_id = event_dict_raw.get("itemId")

        self.remove_event_from_cash(event_id, auth_token)

    # ==================================interval==================================

    @authorized_method
    async def handle_kb_interval_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал событие (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        interval_dict_raw = data.get("result")
        interval_dict = self.kb_interval_from_dict(interval_dict_raw, event)
        kb_interval = KBInterval.from_dict(interval_dict)
        print(kb_interval.krl)

        interval_dict["model"] = kb_interval
        self.add_interval_to_cash(interval_dict, auth_token)

    @authorized_method
    async def handle_kb_interval_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал событие (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        interval_dict_raw = data.get("result")
        interval_dict = self.kb_interval_from_dict(interval_dict_raw, event)
        kb_interval = KBInterval.from_dict(interval_dict)
        print(kb_interval.krl)

        interval_dict["model"] = kb_interval
        self.add_interval_to_cash(interval_dict, auth_token)
        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_interval_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый дублировал интервал (БЗ): ", data)
        current_skills = self.skills.get(auth_token, {})
        interval_dict_raw = data.get("result")
        interval_dict_raw = interval_dict_raw.get("item")
        interval_dict = self.kb_interval_from_dict(interval_dict_raw, event)
        kb_interval = KBInterval.from_dict(interval_dict)
        print(kb_interval.krl)
        interval_dict["model"] = kb_interval
        self.add_interval_to_cash(interval_dict, auth_token)
        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_interval_deleted(self, event: str, data: dict, auth_token: str):
        print("Обучаемый удалил интервал (БЗ): ", data)

        interval_dict_raw = data.get("result")
        interval_id = interval_dict_raw.get("itemId")

        self.remove_interval_from_cash(interval_id, auth_token)

    # ====================================RULE============================
    @authorized_method
    async def handle_kb_rule_created(self, event: str, data: dict, auth_token: str):
        print("Обучаемый создал правило (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        rule_dict_raw = data.get("result")
        rule_dict = self.kb_rule_from_dict(rule_dict_raw, event)
        kb_rule = KBRule.from_dict(rule_dict)
        print(kb_rule.krl)
        rule_dict["model"] = kb_rule
        self.add_rule_to_cash(rule_dict, auth_token)

    @authorized_method
    async def handle_kb_rule_updated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый отредактировал правило (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})

        rule_dict_raw = data.get("result")
        rule_dict = self.kb_rule_from_dict(rule_dict_raw, event)
        rule_id = rule_dict.pop("ruleId", None)
        kb_rule = KBRule.from_dict(rule_dict)
        print(kb_rule.krl)
        rule_dict["ruleId"] = rule_id
        rule_dict["model"] = kb_rule
        self.add_rule_to_cash(rule_dict, auth_token)

    @authorized_method
    async def handle_kb_rule_duplicated(self, event: str, data: dict, auth_token: str):
        print("Обучаемый дублировал правило (БЗ): ", data)
        current_skills = self.skills.get(auth_token, {})
        rule_dict_raw = data.get("result")
        rule_dict_raw = rule_dict_raw.get("item")
        rule_dict = self.kb_rule_from_dict(rule_dict_raw, event)
        kb_rule = KBRule.from_dict(rule_dict)
        rule_dict["model"] = kb_rule
        print(kb_rule.krl)
        self.add_rule_to_cash(rule_dict, auth_token)
        return {
            "skills": current_skills,
            "stage_done": False,
            "message": "Обратите внимание на ошибки",
        }

    @authorized_method
    async def handle_kb_rule_deleted(self, event: str, data: dict, auth_token: str):
        print("Обучаемый удалил правило (БЗ): ", data)

        rule_dict_raw = data.get("result")
        rule_id = rule_dict_raw.get("itemId")

        self.remove_rule_from_cash(rule_id, auth_token)

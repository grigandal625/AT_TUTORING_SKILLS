from at_krl.core.kb_class import KBClass

# from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_type import KBType
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method

from at_tutoring_skills.core.knowledge_base.type.syntax import handle_syntax_mistakes
from ATskills.models import Skill


class ATTutoringKBSkills(ATComponent):

    skills: dict = None
    cash: dict = None

    # # .__dict__()
    # cash = {
    #     "auth_token_value": {
    #         'kb_types': [],
    #         'kb_objects': [],
    #         'kb_events': [],
    #         'kb_intervals': [],
    #         'kb_rules': [],
    #         "mark": 0
    #     }
    # }

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)

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
    # array_name из cash
    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # dest_key поле из которого возвращается результат, например надо получить в результате id значит 'id'
    # key_value: значение с которым сравниваем

    def get_smth_val_by_key(
        self,
        array_name: str,
        search_key: str,
        dest_key: str,
        key_value: str,
        auth_token: str,
    ):

        cash = self.init_cash(auth_token)
        res_item = None

        if array_name in cash:
            for item in cash[array_name]:
                if item.get(search_key) == key_value:
                    res_item = item.get(dest_key)
        if res_item is None:
            print(
                "get_smth_val_by_key",
                " поиск в ",
                array_name,
                " по полю ",
                search_key,
                " по значению",
                key_value,
                " ничего не найдено",
            )
        return res_item

    # name by id
    def get_type_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_types", "typeId", "id", id, auth_token)

    def get_obj_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_objects", "objectId", "id", id, auth_token)

    def get_event_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_events", "eventId", "Name", id, auth_token)

    def get_interval_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key(
            "kb_intervals", "intervalId", "Name", id, auth_token
        )

    def get_rule_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_rules", "ruleId", "id", id, auth_token)

    # id by name

    def get_type_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key("kb_types", "id", "typeId", name, auth_token)

    def get_obj_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_objects", "id", "objectId", id, auth_token)

    def get_event_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_events", "Name", "eventId", id, auth_token)

    def get_interval_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key(
            "kb_intervals", "Name", "intervalId", id, auth_token
        )

    def get_rule_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key("kb_rules", "id", "ruleId", id, auth_token)

    # ============================== get element by name ===================

    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # key_value: значение с которым сравниваем

    def get_smth_by_key(
        self, array_name: str, id_key: str, key_value: str, auth_token: str
    ):
        # Проверяем, что массив существует в self.cash и является списком
        cash = self.init_cash(auth_token)
        res_item = None

        if array_name in cash:
            for item in cash[array_name]:
                if item.get(id_key) == key_value:
                    res_item = item
        if res_item is None:
            print(
                "get_smth_by_key",
                "поиск в ",
                array_name,
                "по полю ",
                id_key,
                "по значению",
                key_value,
                "никого не найдено",
            )
        return res_item

    def get_type_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key("kb_types", "typeId", value, auth_token)

    def get_object_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key("kb_objects", "objectId", value, auth_token)

    def get_event_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key("kb_types", "eventId", value, auth_token)

    def get_interval_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key("kb_intervals", "intervalId", value, auth_token)

    def get_rule_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key("kb_rules", "ruleId", value, auth_token)

    # ==============================get from dict=================== проверено
    @staticmethod
    def kb_type_from_dict(type_dict: dict, event: str) -> dict:

        new_type_dict = {}
        if type_dict:
            new_type_dict["typeId"] = type_dict.get("id")  # id
            new_type_dict["id"] = type_dict.get("kb_id")  # name
            new_type_dict["meta"] = {1: "string", 2: "number", 3: "fuzzy"}[
                type_dict.get("meta")
            ]
            new_type_dict["desc"] = type_dict.get("comment")

            if event != "kbTypes/create" and event != "kbTypes/delete":
                if type_dict["meta"] == 1:
                    new_type_dict["values"] = [
                        v["data"] for v in type_dict["kt_values"]
                    ]
                    new_type_dict["from"], new_type_dict["to"] = None, None
                    new_type_dict["membership_functions"] = None

                elif type_dict["meta"] == 2:
                    new_type_dict["values"] = None
                    new_type_dict["from"], new_type_dict["to"] = [
                        v["data"] for v in type_dict["kt_values"][:2]
                    ]
                    new_type_dict["membership_functions"] = None

                elif type_dict["meta"] == 3:
                    new_type_dict["values"] = None
                    new_type_dict["from"], new_type_dict["to"] = None, None
                    new_type_dict["membership_functions"] = [
                        {
                            "name": v["data"]["name"],
                            "min": v["data"]["max"],
                            "max": v["data"]["min"],
                            "points": [
                                {
                                    "x": p["x"],
                                    "y": p["y"],
                                }
                                for p in v["data"]["points"]
                            ],
                        }
                        for v in type_dict["kt_values"]
                    ]

                else:
                    print("ошибка, базовый тип")
            # kb_type = KBType.from_dict(new_type_dict)
            # print(kb_type.krl)
        else:
            print("ошибка, type_dict пуст")
        return new_type_dict

    def kb_object_from_dict(
        self, object_dict: dict, event: str, auth_token: str
    ) -> dict:

        new_object_dict = {}

        if object_dict:
            new_object_dict["objectId"] = object_dict.get("id")  # id
            new_object_dict["id"] = object_dict.get("kb_id")  # name
            new_object_dict["group"] = object_dict.get("group")
            new_object_dict["desc"] = object_dict.get("comment")

            if event != "kbObjects/create" and event != "kbObjects/delete":
                new_object_dict["properties"] = [
                    {
                        "id": item["kb_id"],
                        "type": self.get_type_name_by_id(
                            item["type"], auth_token
                        ),  # впихнуть функцию имя по id
                        "desc": item["comment"] if item["comment"] is not None else "",
                        "source": item["kb_id"],
                        "tag": "property",
                        "properties_instances": [],
                    }
                    for item in object_dict["ko_attributes"]
                ]
            kb_object = KBClass.from_dict(new_object_dict)
            print(kb_object.krl)
        else:
            print("ошибка, type_dict пуст")

        return new_object_dict

    @staticmethod
    def kb_event_from_dict(event_dict: dict, event: str) -> dict:
        # event_dict = data.get('result')

        new_event_dict = {}
        if event_dict:
            new_event_dict["eventId"] = event_dict["id"]
            new_event_dict["tag"] = "Event"
            new_event_dict["Name"] = event_dict.get("kb_id")
            if event != "kbEvents/create" and event != "kbEvents/delete":
                new_event_dict["Formula"] = event_dict.get("occurance_condition")
        else:
            print("ошибка, type_dict пуст")
        return new_event_dict

    @staticmethod
    def kb_interval_from_dict(interval_dict: dict, event: str) -> dict:

        # interval_dict = data.get('result')
        new_interval_dict = {}
        if interval_dict:
            new_interval_dict["intervalId"] = interval_dict["id"]
            new_interval_dict["Name"] = interval_dict.get("kb_id")
            if event != "kbIntervals/create" and event != "kbIntervals/delete":
                new_interval_dict["Open"] = interval_dict.get("open")
                new_interval_dict["Close"] = interval_dict.get("close")
        else:
            print("ошибка, type_dict пуст")
        return new_interval_dict

    def kb_rule_from_dict(self, rule_dict: dict, event: str):
        new_rule_dict = {}

        if rule_dict:

            new_rule_dict["ruleId"] = rule_dict["id"]  # проверить!!!!!!!!!!!!!!
            new_rule_dict["id"] = rule_dict.get("kb_id")
            new_rule_dict["condition"] = rule_dict.get("condition")
            new_rule_dict["meta"] = "simple"

            new_rule_dict["instructions"] = []
            new_rule_dict["else_instructions"] = []
            if event != "KBrules/create":
                if (
                    "kr_instructions" in rule_dict
                    and rule_dict["kr_instructions"] is not None
                ):
                    for i in rule_dict.get("kr_instructions"):
                        new_rule_dict["instructions"].append(i)
                if (
                    "kr_else_instructions" in rule_dict
                    and rule_dict["kr_else_instructions"] is not None
                ):
                    for i in rule_dict.get("kr_else_instructions"):
                        new_rule_dict["else_instructions"].append(i)
            new_rule_dict["desc"] = rule_dict.get("comment")

            return new_rule_dict

    # ==============================calc elements=========================== проверено

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

    # =============================idx by name===================

    def get_index_by_smth(
        self, array_name: str, id_key: str, name: str, auth_token: str
    ) -> int:

        cash = self.init_cash(auth_token)
        res_index = None
        for index, item in enumerate(self.cash[auth_token][array_name]):

            if item.get(id_key) == name:  # смирение что это имя
                # return index
                res_index = index

        # self.cash[auth_token] = cash
        return res_index

    def get_type_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_smth("kb_types", "id", name, auth_token)

    def get_object_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_smth("kb_objects", "id", name, auth_token)

    def get_event_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_smth("kb_events", "Name", name, auth_token)

    def get_interval_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_smth("kb_intervals", "Name", name, auth_token)

    def get_rule_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_smth("kb_rules", "id", name, auth_token)

    # ============================== add to cash ====================================
    def add_to_cash(self, add_field: str, name_key: str, data: dict, auth_token: str):
        cash = self.init_cash(auth_token)
        name = data.get(name_key)
        id = self.get_index_by_smth(add_field, name_key, name, auth_token)
        if id is not None:
            cash[add_field][id] = data
        else:
            cash[add_field].append(data)
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
    async def handle_knowledge_base_created(
        self, event: str, data: dict, auth_token: str
    ):
        print("Обучаемый создал пустой тип (БЗ): ", data)
        self.init_cash(auth_token)
        current_skills = self.skills.get(auth_token, {})

    @authorized_method
    async def handle_knowledge_base_updated(
        self, event: str, data: dict, auth_token: str
    ):
        print("Обучаемый создал пустой тип (БЗ): ", data)

        current_skills = self.skills.get(auth_token, {})
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

        try:
            KBTypeService.handle_lexic_mistakes(user_id, kb_type)
        except BaseException as e:
            raise ValueError(f"Handle KB Type Created: Lexic Mistakes: {e}") from e

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

        current_skills = self.skills.get(auth_token, {})

        print(data)
        object_dict_raw = data.get("result")
        object_dict = self.kb_object_from_dict(object_dict_raw, event, auth_token)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)
        object_dict["model"] = kb_object
        self.add_object_to_cash(object_dict, auth_token)

    @authorized_method
    async def handle_kb_object_duplicated(
        self, event: str, data: dict, auth_token: str
    ):
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
    async def handle_kb_interval_duplicated(
        self, event: str, data: dict, auth_token: str
    ):
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

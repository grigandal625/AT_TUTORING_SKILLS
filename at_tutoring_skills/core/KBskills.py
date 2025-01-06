from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from at_krl.core.kb_type import KBType
from  at_krl.core.kb_class import KBClass
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
# from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_rule import KBRule
from .api_client import get_skill, get_skills, get_tasks, get_task, get_reaction, get_event

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
        
        self.skills = {} # временное хранилище, тут лучше подключить БД или что-то
        self.cash = {}

    def init_cash(self, auth_token: str):
        if auth_token not in self.cash:
            self.cash[auth_token] = {}
        if 'kb_types' not in self.cash[auth_token]:
            self.cash[auth_token]['kb_types'] = []
        if 'kb_objects' not in self.cash[auth_token]:
            self.cash[auth_token]['kb_objects'] = []
        if 'kb_events' not in self.cash[auth_token]:
            self.cash[auth_token]['kb_events'] = []
        if 'kb_intervals' not in self.cash[auth_token]:
            self.cash[auth_token]['kb_intervals'] = []
        if 'kb_rules' not in self.cash[auth_token]:
            self.cash[auth_token]['kb_rules'] = []
        return self.cash[auth_token]
    
# =================================== det value from element by key ===========================
    # array_name из cash
    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # dest_key поле из которого возвращается результат, например надо получить в результате id значит 'id'
    # key_value: значение с которым сравниваем 

    def get_smth_val_by_key(self, array_name: str, search_key: str, dest_key: str, key_value: str, auth_token: str):
        
        if array_name in self.cash and array_name in self.cash[auth_token]:
            for item in self.cash[array_name]:
                if item.get(search_key) == key_value:
                    return item.get(dest_key)
        else: 
            print('не найдено')
            return None

# name by id  
    def get_type_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_types', 'typeId', 'id', id, auth_token)

    def get_obj_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_objects', 'objectId', 'id', id, auth_token)

    def get_event_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_events', 'eventId', 'Name', id, auth_token)
    
    def get_interval_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_intervals', 'intervalId', 'Name', id, auth_token)
    
    def get_rule_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_rules', 'ruleId', 'id', id, auth_token)
    
# id by name

    def get_type_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('kb_types', 'id', 'typeId', name, auth_token)

    def get_obj_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_objects', 'id', 'objectId', id, auth_token)

    def get_event_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_events', 'Name', 'eventId', id, auth_token)
    
    def get_interval_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_intervals', 'Name', 'intervalId', id, auth_token)
    
    def get_rule_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('kb_rules', 'id', 'ruleId', id, auth_token)    


# ============================== get element by name ===================

    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # key_value: значение с которым сравниваем 

    def get_smth_by_key(self, array_name: str, id_key: str, key_value: str, auth_token: str):
        # Проверяем, что массив существует в self.cash и является списком

        if auth_token in self.cash and array_name in self.cash[auth_token]:
            for item in self.cash[array_name]:
                if item.get(id_key) == key_value:
                    return item
        else:
            return None
    
    def get_type_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key('kb_types', 'typeId', value, auth_token)
    
    def get_object_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key('kb_objects', 'objectId', value, auth_token) 
    
    def get_event_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key('kb_types', 'eventId', value, auth_token)
    
    def get_interval_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key('kb_intervals', 'intervalId', value, auth_token)

    def get_rule_by_id(self, value: str, auth_token: str):
        return self.get_smth_by_key('kb_rules', 'ruleId', value, auth_token)

# ==============================get from dict=================== проверено 
    @staticmethod
    def kb_type_from_dict(type_dict: dict, event: str) -> dict:

        new_type_dict ={}
        if type_dict:
            new_type_dict['typeId'] = type_dict.get('id') #id
            new_type_dict['id'] = type_dict.get('kb_id') #name
            new_type_dict['meta'] = {1: "string", 2: "number", 3: "fuzzy"}[type_dict.get('meta')]
            new_type_dict['desc'] = type_dict.get('comment')

            if event !='kbTypes/create':
                if type_dict['meta']  == 1 :
                    new_type_dict['values'] = [v['data'] for v in type_dict["kt_values"]]
                    new_type_dict['from'], new_type_dict['to'] = None, None
                    new_type_dict['membership_functions'] = None

                elif type_dict['meta'] == 2:
                    new_type_dict['values'] = None
                    new_type_dict['from'], new_type_dict['to'] =  [v['data'] for v in type_dict["kt_values"][:2]]
                    new_type_dict['membership_functions'] = None

                elif type_dict['meta'] == 3 :
                    new_type_dict['values'] = None
                    new_type_dict['from'], new_type_dict['to'] = None, None
                    new_type_dict['membership_functions'] = [ 
                    {
                        'name': v['data']['name'],
                        'min' : v['data']['max'],
                        'max' : v['data']['min'],
                        'points' : [
                            {
                                'x': p['x'],
                                'y': p['y'],
                            } for p in v['data']['points']
                        ],
                    } for v in type_dict["kt_values"]
                    ]

                else:
                    print('ошибка, базовый тип')
            kb_type = KBType.from_dict(new_type_dict)
            print(kb_type.krl)
        else: 
            print('ошибка, type_dict пуст')
        return new_type_dict
    
    # @staticmethod
    def kb_object_from_dict(self, data: dict, event: str)-> dict:
        
        object_dict = data.get('result')
        new_object_dict = {}

        if object_dict:
            new_object_dict['objectId'] = object_dict.get('id') # id
            new_object_dict['id'] = object_dict.get('kb_id') # name
            new_object_dict['group'] = object_dict.get('group')
            new_object_dict['desc'] = object_dict.get('comment')

            if event != "kbObjects/create":
                new_object_dict['properties'] = [
                    {
                        'id' : item['kb_id'],
                        'type' : self.get_type_name_by_id(item['type']), # впихнуть функцию имя по id
                        'desc': item['comment'] if item['comment'] is not None else '',
                        'source' : item['kb_id'],
                        "tag": "property",
                        "properties_instances": [],
                    }
                    for item in object_dict['ko_attributes']
                ]
            kb_object = KBClass.from_dict(new_object_dict)
            print(kb_object.krl)
        else: 
            print('ошибка, type_dict пуст')

        return new_object_dict 
    
    @staticmethod
    def kb_event_from_dict(data: dict, event: str)-> dict:
        event_dict = data.get('result')
        new_event_dict = {}
        if event_dict:
            new_event_dict['eventId'] = event_dict['id']
            new_event_dict['tag'] = "Event"
            new_event_dict['Name'] = event_dict.get('kb_id')
            if event == "kbEvents/update":
                new_event_dict['Formula'] = event_dict.get('occurance_condition')
        else:
            print('ошибка, type_dict пуст') 
        return new_event_dict
    
    @staticmethod
    def kb_interval_from_dict(data: dict, event: str)-> dict:

        interval_dict = data.get('result')
        new_interval_dict ={}
        if interval_dict:      
            new_interval_dict['intervalId'] = interval_dict['id']
            new_interval_dict['Name'] = interval_dict.get('kb_id')
            if event == "kbIntervals/update":
                new_interval_dict['Open'] = interval_dict.get('open')
                new_interval_dict['Close'] = interval_dict.get('close')
        else:
            print('ошибка, type_dict пуст') 
        return new_interval_dict
        
# ==============================calc elements=========================== проверено
    
    def calc_elements(self, array_name, auth_token: str):
        return len(self.cash[auth_token][array_name])

    def calc_kb_types(self, auth_token: str):
        return self.calc_elements ('kb_types', auth_token)
    
    
    def calc_kb_objects(self, auth_token: str ):
        return self.calc_elements('kb_objects', auth_token)
    
    def calc_kb_events(self, auth_token: str ):
        return self.calc_elements('kb_events', auth_token)
    
    def calc_kb_intervals(self, auth_token: str):
        return self.calc_elements('kb_intervals', auth_token)
    
    def calc_kb_rules(self, auth_token: str):
        return self.calc_elements('kb_rules', auth_token)
# =============================idx by name===================

    def get_index_by_name(self, array_name: str, id_key: str, name: str, auth_token: str) -> int:
    
        cash = self.init_cash()
        # a = {}
        # a.get('my_key')
        # a.get('my_key', [])
        # if 'my_key' in a:
        # if self.cash[array_name] 
        for index, item in enumerate(self.cash[array_name]):
            if item.get(id_key) == name: #смирение что это имя
                return index
            
        self.cash[auth_token] = cash
        return -1
    
    def get_type_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_name('kb_types', 'kb_id', name, auth_token)
    
    def get_object_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_name('kb_objects', 'kb_id', name, auth_token)
    
    def get_event_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_name('kb_events', 'Name', name, auth_token)
    
    def get_interval_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_name('kb_intervals', 'Name', name, auth_token)
    
    def get_rule_index_by_name(self, name: str, auth_token: str):
        return self.get_index_by_name('kb_rules', 'kb_id', name, auth_token)

# ============================== add to cash ====================================

    def add_type_to_cash(self, data: dict, auth_token: str):
        cash = self.init_cash()
        name = data.get('id')
        id = self.get_type_index_by_name(name)
        if id != -1:
            cash['kb_types'][id] = data
        else:
            cash['kb_types'].append(data)
        self.cash[auth_token] = cash
        
    def add_object_to_cash(self, data: dict, auth_token: str):
        cash = self.init_cash()
        name = data.get('id')
        id = self.get_object_index_by_name(name)
        if id != -1:
            cash['kb_objects'][id] = data
        else:
            cash['kb_objects'].append(data)
        self.cash[auth_token] = cash
    
    def add_event_to_cash(self, data: dict, auth_token: str):
        cash = self.init_cash()
        name = data.get('Name')
        id = self.get_event_index_by_name(name)
        if id != -1:
            cash['kb_events'][id] = data
        else:
            cash['kb_events'].append(data)
        self.cash[auth_token] = cash
    
    def add_interval_to_cash(self, data: dict, auth_token: str):
        cash = self.init_cash()
        name = data.get('Name')
        id = self.get_interval_index_by_name(name)
        if id != -1:
            cash['kb_intervals'][id] = data
        else:
            cash['kb_intervals'].append(data)
        self.cash[auth_token] = cash

    def add_rule_to_cash(self, data: dict, auth_token: str):
        cash = self.init_cash()
        name = data.get('id')
        id = self.get_rule_index_by_name(name)
        if id!= -1:
            cash['kb_rules'][id] = data
        else:
            cash['kb_rules'].append(data)
        self.cash[auth_token] = cash


# =================================== kb ========================================
   
    @authorized_method
    async def handle_knowledge_base_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        self.init_cash()
        current_skills = self.skills.get(auth_token, {})


    @authorized_method
    async def handle_knowledge_base_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})          
        self.init_cash()    

    @authorized_method
    async def handle_kb_types_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка типов ', data)
        types_array = data['result']['items']
        for item in types_array:
            type_dict = self.kb_type_from_dict(item, event)
            self.add_type_to_cash(type_dict, auth_token)
            type_dict = {}

          
# ============================= type ===================
    
    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})

        data = data['result']
        type_dict = self.kb_type_from_dict(data, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.cash['kb_types'].append(type_dict) # запись в кэш
        
        # current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        
        # self.skills[auth_token] = current_skills
        
        if current_skills['kb_types'] >= 50:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    

    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})

        type_dict = self.kb_type_from_dict(data, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.cash['kb_types'].append(type_dict)

        # current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        
        # временная заглушка, что навыки набраны
        current_skills['kb_types'] = 60
        
        self.skills[auth_token] = current_skills
        
        if current_skills['kb_types'] >= 50:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    

    #==================================object =========================================== 
    @authorized_method
    async def handle_kb_object_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал объект (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        print(data)

        object_dict = self.kb_object_from_dict(data, event)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал объект (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        object_dict = self.kb_object_from_dict(data, event)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)


    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        print(data)
        event_dict= self.kb_event_from_dict(data, event)
        kb_event = KBEvent.from_dict(event_dict)   
        print (kb_event.krl)


    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        event_dict= self.kb_event_from_dict(data, event)
        kb_event = KBEvent.from_dict(event_dict)   
        print (kb_event.krl)

    #==================================interval==================================
   
    @authorized_method
    async def handle_kb_interval_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        interval_dict  = self.kb_interval_from_dict(data, event)
        kb_interval = KBInterval.from_dict(interval_dict)   
        print (kb_interval.krl)


    @authorized_method
    async def handle_kb_interval_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        # print(data)
        interval_dict  = self.kb_interval_from_dict(data, event)
        kb_interval = KBInterval.from_dict(interval_dict)   
        print (kb_interval.krl)

    #====================================RULE============================
    @authorized_method 
    async def handle_kb_rule_created(self, event: str, data: dict, auth_token: str):

        print('Обучаемый создал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        rule_dict  = self.kb_rule_from_dict(data, event)
        kb_rule = KBInterval.from_dict(rule_dict)   
        print (kb_rule.krl)

    @authorized_method
    async def handle_kb_rule_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})
        print(data)

        rule_dict = data.get('result')
        if rule_dict:
            
            rule_dict['ruleId'] = rule_dict['item']['id'] # проверить!!!!!!!!!!!!!!
            rule_dict['id'] =  rule_dict.get('kb_id')
            rule_dict['condition'] = rule_dict.get('condition')
            rule_dict['meta'] = 'simple'

            rule_dict['instructions']=[]
            rule_dict['else_instructions'] =[]
            if 'kr_instructions' in rule_dict and rule_dict['kr_instructions'] is not None:
                for i in rule_dict.get('kr_instructions'):
                    rule_dict['instructions'].append(i)
            if 'kr_else_instructions' in rule_dict and rule_dict['kr_else_instructions']is not None:
                for i in rule_dict.get('kr_else_instructions'):
                    rule_dict['else_instructions'].append(i)
            rule_dict['desc'] = rule_dict.get('comment')
            kb_rule = KBRule.from_dict(rule_dict)
            print (kb_rule.krl)
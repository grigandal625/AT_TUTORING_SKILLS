from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from at_krl.core.kb_type import KBType
from  at_krl.core.kb_class import KBClass
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_rule import KBRule

class ATTutoringSkills(ATComponent):

    skills: dict = None

    # .__dict__()
    kash = {
        'auth_token': None,
        'mark' : None,
        'kb_types': [],
        'kb_objects': [],
        'kb_events': [],
        'kb_intervals': [],
        'kb_rules': [],
    }
    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        
        self.skills = {} # временное хранилище, тут лучше подключить БД или что-то

# =================================== det value from element by key ===========================
    # array_name из kash
    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # dest_key поле из которого возвращается результат, например надо получить в результате id значит 'id'
    # key_value: значение с которым сравниваем 

    def get_smth_val_by_key(self, array_name: str, search_key: str, dest_key: str, key_value: str):
        
        if array_name in self.kash and isinstance(self.kash[array_name], list):
            for item in self.kash[array_name]:
                if item.get(search_key) == key_value:
                    return item.get(dest_key)
        else: 
            print('не найдено')
            return None

# name by id  
    def get_type_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_types', 'typeId', 'id', id)

    def get_obj_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_objects', 'objectId', 'id', id)

    def get_event_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_events', 'eventId', 'Name', id)
    
    def get_interval_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_intervals', 'intervalId', 'Name', id)
    
    def get_rule_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_rules', 'ruleId', 'id', id)
    
# id by name

    def get_type_id_by_name(self, name: str):
        return self.get_smth_val_by_key('kb_types', 'id', 'typeId', name)

    def get_obj_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_objects', 'id', 'objectId', id)

    def get_event_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_events', 'Name', 'eventId', id)
    
    def get_interval_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_intervals', 'Name', 'intervalId', id)
    
    def get_rule_name_by_id(self, id: str):
        return self.get_smth_val_by_key('kb_rules', 'id', 'ruleId', id)    


# ============================== get element by name ===================

    # search_key поле по которому происходит сравнение, например проверем равенство имен значит 'Name'
    # key_value: значение с которым сравниваем 

    def get_smth_by_key(self, array_name: str, id_key: str, key_value: str):
        # Проверяем, что массив существует в self.kash и является списком
        if array_name in self.kash and isinstance(self.kash[array_name], list):
            for item in self.kash[array_name]:
                if item.get(id_key) == key_value:
                    return item
        else:
            return None
    
    def get_type_by_id(self, value: str):
        return self.get_smth_by_key('kb_types', 'typeId', value)
    
    def get_object_by_id(self, value: str):
        return self.get_smth_by_key('kb_objects', 'objectId', value) 
    
    def get_event_by_id(self, value: str):
        return self.get_smth_by_key('kb_types', 'eventId', value)
    
    def get_interval_by_id(self, value: str):
        return self.get_smth_by_key('kb_intervals', 'intervalId', value)

    def get_rule_by_id(self, value: str):
        return self.get_smth_by_key('kb_rules', 'ruleId', value)

# ==============================get from dict===================
    @staticmethod
    def kb_type_from_dict(data: dict, event: str) -> dict:
        type_dict = data.get('result')
        if type_dict:
            type_dict['typeId'] = type_dict['item']['id']
            type_dict['id'] = type_dict.get('kb_id')
            type_dict['meta'] = {1: "string", 2: "number", 3: "fuzzy"}[type_dict.get('meta')]
            type_dict['desc'] = type_dict.get('comment')

            if data['event'] =="kbObjects/update":
                if type_dict['meta']  == 1 :
                    type_dict['values'] = [v['data'] for v in type_dict["kt_values"]]
                    type_dict['from'], type_dict['to'] = None, None
                    type_dict['membership_functions'] = None

                elif type_dict['meta'] == 2:
                    type_dict['values'] = None
                    type_dict['from'], type_dict['to'] =  [v['data'] for v in type_dict["kt_values"][:2]]
                    type_dict['membership_functions'] = None

                elif type_dict['meta'] == 3 :
                    type_dict['values'] = None
                    type_dict['from'], type_dict['to'] = None, None
                    type_dict['membership_functions'] = [ 
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
            kb_type = KBType.from_dict(type_dict)
            print(kb_type.krl)
        else: 
            print('ошибка, type_dict пуст')
        return type_dict
    
    @staticmethod
    def kb_class_from_dict(data: dict, event: str)-> dict:
        
        object_dict = data.get('result')
        if object_dict:
            object_dict['objectId'] = object_dict['item']['id']
            object_dict['id'] = object_dict.get('kb_id')
            object_dict['group'] = object_dict.get('group')
            object_dict['desc'] = object_dict.get('comment')

            if event == "kbObjects/update":
                object_dict['properties'] = [
                    {
                        'id' : item['kb_id'],
                        'type' : item['type'],
                        'desc': item['comment'] if item['comment'] is not None else '',
                        'source' : item['kb_id'],
                        "tag": "property",
                        "properties_instances": [],
                    }
                    for item in object_dict['ko_attributes']
                ]
            kb_object = KBClass.from_dict(object_dict)
            print(kb_object.krl)
        else: 
            print('ошибка, type_dict пуст')

        return object_dict 
    
    @staticmethod
    def kb_event_from_dict(data: dict, event: str)-> dict:
        event_dict = data.get('result')
        if event_dict:
            event_dict['eventId'] = event_dict['id']
            event_dict['tag'] = "Event"
            # event_dict['id'] = event_dict['item'].get('kb_id')
            event_dict['Name'] = event_dict['item'].get('kb_id')
            if event == "kbEvents/update":
                event_dict['Formula'] = event_dict.get('occurance_condition')
        else:
            print('ошибка, type_dict пуст') 
        return event_dict
    
    @staticmethod
    def kb_interval_from_dict(data: dict, event: str)-> dict:

        interval_dict = data.get('result')
        if interval_dict:      
            interval_dict['intervalId'] = interval_dict['id']
            interval_dict['Name'] = interval_dict.get('kb_id')
            if event == "kbIntervals/update":
                interval_dict['Open'] = interval_dict.get('open')
                interval_dict['Close'] = interval_dict.get('close')
        else:
            print('ошибка, type_dict пуст') 
        return interval_dict
        
# ==============================calc elements===========================
    
    def calc_elements(self, array_name):
        return len(self.kash[array_name])

    def calc_kb_type_skills(self ):
        return self.calc_elements('kb_type')
    
    def calc_kb_object_skills(self ):
        return self.calc_elements('kb_objects')
    
    def calc_kb_event_skills(self ):
        return self.calc_elements('kb_events')
    
    def calc_kb_interval_skills(self):
        return self.calc_elements('kb_intervals')
    
    def calc_kb_rule_skills(self):
        return self.calc_elements('kb_rules')
# =============================idx by name===================

    def get_index_by_name(self, array_name: str, id_key: str, name: str) -> int:
    
        for index, item in enumerate(self.kash[array_name]):
            if item.get(id_key) == name: #смирение что это имя
                return index
        return -1
    
    def get_type_id_by_name(self, name: str):
        return self.get_index_by_name('kb_types', 'kb_id', name)
    
    def get_object_id_by_name(self, name: str):
        return self.get_index_by_name('kb_objects', 'kb_id', name)
    
    def get_event_id_by_name(self, name: str):
        return self.get_index_by_name('kb_events', 'Name', name)
    
    def get_interval_id_by_name(self, name: str):
        return self.get_index_by_name('kb_intervals', 'Name', name)
    
    def get_rule_id_by_name(self, name: str):
        return self.get_index_by_name('kb_rules', 'kb_id', name)

# ============================== add to kash ====================================

    # def add_to_kash(self, data: dict, array_name: str):



        
            

# =================================== kb ========================================
   
   
    @authorized_method
    async def handle_kb_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})
        
        current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        self.kash['kb_types'] = [ ]
        self.kash['kb_objects'] = []
        self.kash['kb_operations'] = []
        self.kash['kb_rules'] = []
# ============================= type ===================
    
    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})
        
        type_dict = self.kb_type_from_dict(data, event)
        kb_type = KBType.from_dict(type_dict)
        print(kb_type.krl)
        self.kash['kb_type'].append(type_dict) # запись в кэш
        
        current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        
        self.skills[auth_token] = current_skills
        
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

        object_dict = self.kb_class_from_dict(data)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)

    @authorized_method
    async def handle_kb_object_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал объект (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        object_dict = self.kb_class_from_dict(data)
        kb_object = KBClass.from_dict(object_dict)
        print(kb_object.krl)


    # =================================event================================
    @authorized_method
    async def handle_kb_event_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        print(data)
        event_dict= self.kb_interval_from_dict(data, event)
        kb_event = KBEvent.from_dict(event_dict)   
        print (kb_event.krl)


    @authorized_method
    async def handle_kb_event_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал событие (БЗ): ', data)

        current_skills = self.skills.get(auth_token, {})

        event_dict= self.kb_interval_from_dict(data, event)
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
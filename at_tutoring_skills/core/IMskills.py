from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
# далее делаешь импорт всех классов, спроси влада что именно нужно

class ATTutoringIMSkills(ATComponent):
    skills: dict = None
    cash: dict = None

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        
        self.skills = {} # временное хранилище, тут лучше подключить БД или что-то
        self.cash = {}        
        
    def init_cash(self, auth_token: str):
        if auth_token not in self.cash:
            self.cash[auth_token] = {}
        if 'im_resourceTypes' not in self.cash[auth_token]:
            self.cash[auth_token]['im_resourceTypes'] = []
        if 'im_resources' not in self.cash[auth_token]:
            self.cash[auth_token]['im_resources'] = []
        if 'im_templates' not in self.cash[auth_token]:
            self.cash[auth_token]['im_templates'] = []
        if 'im_templateUsages' not in self.cash[auth_token]:
            self.cash[auth_token]['im_templateUsages'] = []
        if 'im_funcs' not in self.cash[auth_token]:
            self.cash[auth_token]['im_funcs'] = []
        return self.cash[auth_token]
        
# ==============================get from dict===================


    # простые методы класса, если есть работа с cash делай их
    def get_operation_name_by_id(self, id: str):
        return 0
        

# =================================== det value from element by key ===========================
    # Универсальный метод для поиска значений по ключам
    def get_smth_val_by_key(self, array_name: str, search_key: str, dest_key: str, key_value: str, auth_token: str):
        cash = self.init_cash(auth_token)
        res_item = None

        if array_name in cash:
            for item in cash[array_name]:
                if item.get(search_key) == key_value:
                    res_item = item.get(dest_key)
        if res_item is None: 
            print('get_smth_val_by_key', 
                ' поиск в ', array_name, 
                ' по полю ', search_key,
                ' по значению', key_value, ' ничего не найдено')
        return res_item
    
    def get_smth_by_key(self, array_name: str, id_key: str, key_value: str, auth_token: str):
        # Проверяем, что массив существует в self.cash и является списком
        cash = self.init_cash(auth_token)
        res_item = None

        if array_name in cash:
            for item in cash[array_name]:
                if item.get(id_key) == key_value:
                    res_item = item
        if res_item is None:
            print('get_smth_by_key', 
                  'поиск в ', array_name, 
                  'по полю ', id_key,
                  'по значению', key_value,'никого не найдено')
        return res_item
    
    # def get_attr_name_bytypeid_byatrrid(self, type_id: str, atrr_id: str, auth_token):
    #     print()
    #     type = self.get_smth_by_key('im_resourceTypes','typeId', type_id, auth_token )
    #     attr_name = None
    #     if type is not None:
    #         for attr in type['attributes_processed']:
    #             if attr.get('attributeId'):
    #                 attr_name = attr.get('name')
    #         if attr_name is None:
    #             print("Аттрибут с указанным id не найден")
    #     else:
    #         print("тип не найден")

    #     return attr_name


    # Методы для получения Name по id
    def get_im_resourceType_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('im_resourceTypes', 'resourceTypeId', 'Name', id, auth_token)

    def get_im_resource_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('im_resources', 'resourceId', 'Name', id, auth_token)

    def get_im_template_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('im_templates', 'templateId', 'Name', id, auth_token)

    def get_im_templateUsage_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('im_templateUsages', 'templateUsageId', 'Name', id, auth_token)

    def get_im_func_name_by_id(self, id: str, auth_token: str):
        return self.get_smth_val_by_key('im_funcs', 'funcId', 'Name', id, auth_token)

    # Методы для получения id по Name
    def get_im_resourceType_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('im_resourceTypes', 'Name', 'resourceTypeId', name, auth_token)

    def get_im_resource_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('im_resources', 'Name', 'resourceId', name, auth_token)

    def get_im_template_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('im_templates', 'Name', 'templateId', name, auth_token)

    def get_im_templateUsage_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('im_templateUsages', 'Name', 'templateUsageId', name, auth_token)

    def get_im_func_id_by_name(self, name: str, auth_token: str):
        return self.get_smth_val_by_key('im_funcs', 'Name', 'funcId', name, auth_token)

# ============================== add to cash ====================================
   


   
# ==============================get from dict===================
    @staticmethod
    def im_resourceTypes_from_dict(resourcetype: dict, event: str) -> dict:
        new_resourcetype ={}
        if resourcetype:
            new_resourcetype['typeId'] = resourcetype['id']  # Переносим ID
            new_resourcetype['meta'] = {1: 'constant', 2: 'temporal'}.get(resourcetype['type'], 0)  # Добавлен новый тип
            new_resourcetype['attributes_processed'] = []

            # Обработка атрибутов
            for attr in resourcetype.get('attributes', []):
                processed_attr = {
                    'attributeId': attr['id'],
                    'name': attr['name'],
                    'type': attr.get('type', None),
                    'default': attr.get('default_value')
                }
                # Обработка enum-атрибутов
                if attr['type'] == 4:
                    processed_attr['enum_values'] = attr.get('enum_values_set', [])

                new_resourcetype['attributes_processed'].append(processed_attr)
        else:
            print("Ошибка: resourcetype пуст")
        return new_resourcetype

    def im_resources_from_dict(self, resource: dict, event: str,auth_token) -> dict:
        new_resource = {}
        
        if resource:
            # Базовая информация о ресурсе
            new_resource['resourceId'] = resource.get('id')
            new_resource['modelId'] = resource.get('model_id')
            new_resource['resourceTypeId'] = resource.get('resource_type_id')
            new_resource['resourceTypeName'] = self.get_smth_by_key('im_resourceTypes', 'typeId',new_resource['resourceTypeId'], auth_token )
            new_resource['name'] = resource.get('name')
            new_resource['traceable'] = resource.get('to_be_traced', False)
            new_resource['attributes_processed'] = []

            # Обработка атрибутов ресурса
            for attr in resource.get('attributes', []):
                processed_attr = {
                    'attributeId': attr.get('rta_id'),
                    'attributeName': attr.get('name'),
                    'attributeValue': attr.get('value')
                }
                new_resource['attributes_processed'].append(processed_attr)
            
            # События
            if event == "resources/create":
                print(f"Ресурс создан: {new_resource['name']} (ID: {new_resource['resourceId']})")
            elif event == "resources/update":
                print(f"Ресурс обновлен: {new_resource['name']} (ID: {new_resource['resourceId']})")
            else:
                print("Неизвестное событие")
        else:
            print("Ошибка: ресурс пуст")
        return new_resource


    @staticmethod
    def im_func_from_dict(func: dict, event: str) -> dict:
        new_func = {}
        
        if func:
            # Базовая информация о функции
            new_func['funcId'] = func.get('id')
            new_func['name'] = func.get('name')
            new_func['returnType'] = func.get('ret_type')
            new_func['parameters_processed'] = []
            new_func['body'] = func.get('body')

            # Обработка параметров функции
            for param in func.get('params', []):
                processed_param = {
                    'paramName': param['name'],
                    'paramType': param['type']
                }
                new_func['parameters_processed'].append(processed_param)

        else:
            print("Ошибка: функция не найдена")

        return new_func
    
    def im_template_from_dict(self, dict: str, event: str, auth_token):
        new_templateUsage = {}
        #проверено на create, update
        # можно реорганизовать как тебе удобно
        
        #извлекается вне хависимости от типа
        dict1 = dict.get('meta')

        new_templateUsage['id'] = dict1.get('id')
        new_templateUsage['name'] = dict1.get('name')
        new_templateUsage['type'] = dict1.get('type')
        

        new_templateUsage['related_resources'] = []
        if dict1.get('rel_resources', None) is not None:
            for res in dict1['rel_resources']:
                rel_res = {
                    'name':  res.get('name'),
                    'resource_type_id' : res.get('resource_type_id'),
                    'resource_type_name' : self.get_smth_by_key('im_resourceTypes', 'typeId',res.get('resource_type_id'), auth_token )
                }
                new_templateUsage['related_resources'].append(rel_res)

        #дальше идет обработка случаев
        if new_templateUsage['meta']['type'] == 'irregular_event':
            
            dict2 = dict.get('generator')
            if dict2 is not None:
                new_templateUsage['generator'] = {
                    'type' : dict2.get('type'),
                    'value' : dict2.get('value'),
                    'dispersion' : dict2.get('dispersion')
                    }
            dict3 = dict.get('body')
            if dict3 is not None:
                new_templateUsage['body'] ={
                    'body' : dict3.get('body'),
                    }
                
        if new_templateUsage['meta']['type'] == 'operation':
            new_templateUsage['generator'] ={}
            dict3 = dict.get('body')
            new_templateUsage['body'] ={
                'delay': dict3.get('delay'),
                'condition': dict3.get('condition'),
                'body_before' : dict3.get('body_before'),
                'body_after' : dict3.get('body_after')
                }
            
        if new_templateUsage['meta']['type'] == 'rule':
            new_templateUsage['generator'] = {}
            dict3 = dict.get('body')
            new_templateUsage['body'] = {
                'condition': dict3.get('condition'),
                'body': dict3.get('body'), #actions? better naming
            }

        return new_templateUsage
    
    # def im_templateUsage_from_dict(self, dict: str, event: str, auth_token):
        




# ==============================calc elements===========================
    def calc_elements(self, array_name, auth_token: str):
        return len(self.cash[auth_token][array_name])
    
    def calc_im_resourceTypes_skills(self, auth_token: str):
        return self.calc_elements('im_resourceTypes', auth_token)
    
    def calc_im_resources_skills(self, auth_token: str):
        return self.calc_elements('im_resources', auth_token)
    
    def calc_im_templates_skills(self, auth_token: str):
        return self.calc_elements('im_templates', auth_token)

        
    def calc_im_templateUsages_skills(self, auth_token: str):
        return self.calc_elements('im_templateUsages', auth_token)

    def calc_im_funcs_skills(self, auth_token: str):
        return self.calc_elements('im_funcs', auth_token)

# ============================= Cash ===================
    # Получение индекса объекта в кэше по значению
    def get_index_by_smth(self, array_name: str, id_key: str, name: str, auth_token: str) -> int:
        cash = self.init_cash(auth_token)
        res_index = None
        for index, item in enumerate(cash[array_name]):
            if item.get(id_key) == name:  # Сравнение с искомым значением
                res_index = index
        return res_index

    # Добавление объекта в кэш
    def add_to_cash(self, add_field: str, name_key: str, data: dict, auth_token: str):
        cash = self.init_cash(auth_token)
        name = data.get(name_key)
        index = self.get_index_by_smth(add_field, name_key, name, auth_token)
        if index is not None:
            cash[add_field][index] = data  # Обновляем объект, если он уже существует
        else:
            cash[add_field].append(data)  # Добавляем новый объект
        self.cash[auth_token] = cash

    # Удаление объекта из кэша
    def remove_from_cash(self, key_val: str, del_field: str, search_field: str, auth_token: str):
        cash = self.init_cash(auth_token)
        print("Проверка длины перед удалением:", len(cash[del_field]))
        index = self.get_index_by_smth(del_field, search_field, key_val, auth_token)
        if index is not None:
            del cash[del_field][index]  # Удаляем объект по индексу
            print("\nЭлемент удалён. Текущая длина:", len(cash[del_field]))
        else:
            print('Объект не найден')
        self.cash[auth_token] = cash

    # Тип ресурса
    def add_im_resourceType_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash('im_resourceTypes', 'Name', data, auth_token)

    def remove_im_resourceType_from_cash(self, key_val: str, auth_token: str):
        self.remove_from_cash(key_val, 'im_resourceTypes', 'Name', auth_token)

    # Ресурс
    def add_im_resource_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash('im_resources', 'Name', data, auth_token)

    def remove_im_resource_from_cash(self, key_val: str, auth_token: str):
        self.remove_from_cash(key_val, 'im_resources', 'Name', auth_token)
    
    # Образец операции
    def add_im_template_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash('im_templates', 'Name', data, auth_token)

    def remove_im_template_from_cash(self, key_val: str, auth_token: str):
        self.remove_from_cash(key_val, 'im_templates', 'Name', auth_token)

    # Операция
    def add_im_templateUsage_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash('im_templateUsages', 'Name', data, auth_token)

    def remove_im_templateUsage_from_cash(self, key_val: str, auth_token: str):
        self.remove_from_cash(key_val, 'im_templateUsages', 'Name', auth_token)
    
    # Функция
    def add_im_func_to_cash(self, data: dict, auth_token: str):
        self.add_to_cash('im_funcs', 'Name', data, auth_token)

    def remove_im_func_from_cash(self, key_val: str, auth_token: str):
        self.remove_from_cash(key_val, 'im_funcs', 'Name', auth_token)

# =================================== im ======================================== 
    @authorized_method
    async def handle_im_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустую модель (ИМ): ', data)
        self.init_cash(auth_token)
        current_skills = self.skills.get(auth_token, {})

    @authorized_method
    async def handle_im_resourceTypes_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка типов ресурсов ', data)
        resourceTypes_array = data['result']['items']
        print (resourceTypes_array)
        for item in resourceTypes_array:
            resourceTypes_dict = self.im_resourceTypes_from_dict(item, event)
            self.add_im_resourceTypes_to_cash(resourceTypes_dict, auth_token)
            resourceTypes_dict = {}

    @authorized_method
    async def handle_im_resources_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка ресурсов ', data)
        resources_array = data['result']['items']
        print (resources_array)
        for item in resources_array:
            resource_dict = self.im_resources_from_dict(item, event, auth_token, auth_token)
            self.add_im_resources_to_cash(resource_dict, auth_token)
            resource_dict = {}

    @authorized_method
    async def handle_im_templates_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка образцов операций ', data)
        events_array = data['result']['items']
        for item in events_array:
            event_dict = self.im_templates_from_dict(item, event)
            self.add_event_to_cash(event_dict, auth_token)
            event_dict = {}

    @authorized_method
    async def handle_im_templateUsages_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка операций ', data)
        intervals_array = data['result']['items']
        for item in intervals_array:
            interval_dict = self.im_templateUsages_from_dict(item, event)
            self.add_interval_to_cash(interval_dict, auth_token)
            interval_dict = {}

    @authorized_method
    async def handle_im_funcs_get(self, event: str, data: dict, auth_token: str):
        print('извлечение списка правил ', data)
        funcs_array = data['result']['items']
        for item in funcs_array:
            funcs_dict = self.im_funcs_from_dict(item, event)
            self.add_rule_to_cash(funcs_dict, auth_token)
            funcs_dict = {}

# ============================= Resource Types ===================
    @authorized_method
    async def handle_im_resourceTypes_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип ресурса (ИМ): ', data)
        
        current_skills = self.skills.get(auth_token, {})

        resourcetype_dict = self.im_resourceTypes_from_dict(data, event)
        print('Проверка resourcetype_dict:', resourcetype_dict) # Вывод для проверки
        self.add_im_resourceTypes_to_cash(resourcetype_dict, auth_token) # запись в кэш
        
        # current_skills['im_resourceTypes'] = self.calc_im_resourceTypes_skills(current_skills, data)
        # self.skills[auth_token] = current_skills
        
        if current_skills['im_resourceTypes'] >= 4:
            return {'skills': current_skills, 'stage_done': True}
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_resourceTypes_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал отредактировал тип ресурса (ИМ): ', data)
        
        # current_skills = self.skills.get(auth_token, {})
        # resourcetype_dict = self.im_resourceTypes_from_dict(data, event)
        # print('Проверка resourcetype_dict:', resourcetype_dict) # Вывод для проверки
        
        # self.add_im_resourceTypes_to_cash(resourcetype_dict, auth_token) # запись в кэш
        return {'stage_done': True, 'message': 'Этап создания типов ресурсов пройден. Осуществляется переход к этапу создания ресурсов.'}

    @authorized_method
    async def handle_im_resourceTypes_duplicated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый дублировал тип ресурса (ИМ): ', data)
        
        current_skills = self.skills.get(auth_token, {})

        resourcetype_dict_raw = data.get('result', {}).get('item', {})
        resourcetype_dict = self.im_resourceTypes_from_dict(resourcetype_dict_raw, event)
        print('Проверка resourcetype_dict:', resourcetype_dict)  # Лог для проверки
        
        self.add_im_resourceTypes_to_cash(resourcetype_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    
    @authorized_method
    async def handle_im_resourceTypes_deleted(self, event: str, data: dict, auth_token: str):
        print('Обучаемый удалил тип ресурса (ИМ): ', data)

        resourcetype_dict_raw = data.get('result')
        resourcetype_id = resourcetype_dict_raw.get('resourcetypesId')

        self.remove_im_resourceTypes_from_cash(resourcetype_id, auth_token)

# ============================= Resources ===================
    @authorized_method
    async def handle_im_resources_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал ресурс (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})
        
        resource_dict = self.im_resources_from_dict(data, event, auth_token)
        print('Проверка resource_dict:', resource_dict)
        
        self.add_im_resources_to_cash(resource_dict, auth_token)
        
        if current_skills.get('im_resources', 0) >= 4:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_resources_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал ресурс (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})
        
        resource_dict = self.im_resources_from_dict(data, event, auth_token)
        print('Проверка resource_dict:', resource_dict)
        
        self.update_im_resources_in_cash(resource_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_resources_duplicated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый дублировал ресурс (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})
        
        resource_dict_raw = data.get('result', {}).get('item', {})
        resource_dict = self.im_resources_from_dict(resource_dict_raw, event,auth_token)
        print('Проверка resource_dict:', resource_dict)
        
        self.add_im_resources_to_cash(resource_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_resources_deleted(self, event: str, data: dict, auth_token: str):
        print('Обучаемый удалил ресурс (ИМ):', data)

        resource_dict_raw = data.get('result', {})
        resource_id = resource_dict_raw.get('resourceId')
        
        self.remove_im_resources_from_cash(resource_id, auth_token)

# ============================= Templates ===================
    @authorized_method
    async def handle_im_template_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})

        template_dict = self.im_template_from_dict(data, event)
        print('Проверка template_dict:', template_dict)

        self.add_im_template_to_cash(template_dict, auth_token)

        if current_skills.get('im_templates', 0) >= 4:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_template_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})
        data = data.get('result')
        template_dict = self.im_template_from_dict(data, event, auth_token)
        print('Проверка template_dict:', template_dict)

        self.update_im_template_in_cash(template_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_template_duplicated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый дублировал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})

        template_dict_raw = data.get('result', {}).get('item', {})
        template_dict = self.im_template_from_dict(template_dict_raw, event)
        print('Проверка template_dict:', template_dict)

        self.add_im_template_to_cash(template_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_template_deleted(self, event: str, data: dict, auth_token: str):
        print('Обучаемый удалил образец операции (ИМ):', data)

        template_dict_raw = data.get('result', {})
        template_id = template_dict_raw.get('templateId')

        self.remove_im_template_from_cash(template_id, auth_token)

# ============================= Template Usages ===================
    @authorized_method
    async def handle_im_templateUsages_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})
        data  = data.get('result')
        template_usage_dict = self.im_templateUsages_from_dict(data, event, auth_token)
        print('Проверка template_usage_dict:', template_usage_dict)  # Лог для проверки

        self.add_im_templateUsage_to_cash(template_usage_dict, auth_token)

        if current_skills.get('im_templateUsages', 0) >= 4:
            return {'skills': current_skills, 'stage_done': True}
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_templateUsages_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})

        template_usage_dict = self.im_templateUsages_from_dict(data, event)
        print('Проверка template_usage_dict:', template_usage_dict)  # Лог для проверки

        self.update_im_templateUsage_in_cash(template_usage_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_templateUsages_duplicated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый дублировал образец операции (ИМ):', data)

        current_skills = self.skills.get(auth_token, {})

        template_usage_dict_raw = data.get('result', {}).get('item', {})
        template_usage_dict = self.im_templateUsages_from_dict(template_usage_dict_raw, event)
        print('Проверка template_usage_dict:', template_usage_dict)  # Лог для проверки

        self.add_im_templateUsage_to_cash(template_usage_dict, auth_token)
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}

    @authorized_method
    async def handle_im_templateUsages_deleted(self, event: str, data: dict, auth_token: str):
        print('Обучаемый удалил образец операции (ИМ):', data)

        template_usage_dict_raw = data.get('result', {})
        template_usage_id = template_usage_dict_raw.get('templateUsageId')

        self.remove_im_templateUsage_from_cash(template_usage_id, auth_token)

    # ============================= Funcs ===================
    @authorized_method
    async def handle_im_func_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустую функцию (ИМ): ', data)

        current_skills = self.skills.get(auth_token, {})

        resource_dict = self.im_func_from_dict(data, event)
        print('Проверка type_dict:', resource_dict) # Вывод для проверки
        self.cash['im_funcs'].append(resource_dict) # запись в кэш
        
        # current_skills['im_templateUsages'] = self.calc_im_templateUsages_skills(current_skills, data)
        # self.skills[auth_token] = current_skills
        
        if current_skills['im_templateUsages'] >= 6:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
        

    @authorized_method
    async def handle_im_func_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал функцию (ИМ): ', data)
        
        current_skills = self.skills.get(auth_token, {})

        resource_dict = self.im_func_from_dict(data, event)
        print('Проверка type_dict:', resource_dict) # Вывод для проверки
        
        #, current_skills['im_templateUsages'] = self.calc_im_templateUsages_skills(current_skills, data)
        current_skills['im_funcs'] = 10
        self.skills[auth_token] = current_skills

        if current_skills['im_funcs'] >= 10:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    

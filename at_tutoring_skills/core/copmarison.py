import re
import json
# from skills_data.ATskills.models import Task

class ComparisonResult:
    isEqual : bool = False
    mistakes_count: int = None
    info: None


    def __init__(self, res: bool, count: int):
        self.res = res
        self.count = count

class Comparison:

    @staticmethod
    def normalize_spaces(s):
        """Нормализует пробелы, заменяя несколько подряд идущих пробелов на один."""
        return re.sub(r'\s+', ' ', s.strip())

    @staticmethod   
    def levenshtein_distance(str1: str, str2: str):
        """Вычисляет расстояние Левенштейна между двумя строками с допуском одной опечатки."""
        len_str1, len_str2 = len(str1), len(str2)
        
        # Если одна из строк пуста, то расстояние - это длина другой строки
        if len_str1 == 0:
            return len_str2
        if len_str2 == 0:
            return len_str1
        
        # Создание таблицы для динамического программирования
        dp = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]
        
        # Инициализация первой строки и первого столбца
        for i in range(len_str1 + 1):
            dp[i][0] = i
        for j in range(len_str2 + 1):
            dp[0][j] = j

        # Заполнение таблицы
        for i in range(1, len_str1 + 1):
            for j in range(1, len_str2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,        # Удаление
                    dp[i][j - 1] + 1,        # Вставка
                    dp[i - 1][j - 1] + cost  # Замена
                )

        return dp[len_str1][len_str2]
    
    @staticmethod   
    def compare_strings(str1: str, str2: str):
        """Сравнивает две строки с учётом регистра, одной опечатки и нескольких подряд идущих пробелов."""
        
        # Нормализуем строки, удаляя лишние пробелы
        normalized_str1 = Comparison.normalize_spaces(str1)
        normalized_str2 = Comparison.normalize_spaces(str2)
        
        # Если строки абсолютно идентичны (с учётом нормализации пробелов)
        if normalized_str1 == normalized_str2:
            return True, 0
        
        # Проверяем расстояние Левенштейна с допуском одной ошибки
        edit_distance = Comparison.levenshtein_distance(normalized_str1, normalized_str2)

        return edit_distance
        
    @staticmethod
    def compare_numbers(num1, num2):
        """Сравнивает два числа на равенство."""
        if num1 == num2:
            return ComparisonResult.__init__(True, 0, None)
        else:
            return ComparisonResult.__init__(False, 0, info=[num1, num2])
    # @staticmethod
    # def compare_dicts_by_values(dict1: dict, dict2: dict):
    #     """Сравнивает два словаря по значениям в одинаковых ключах."""
    #     count = 0
    #     for key in dict1:
    #         if key in dict2:
    #             if dict1[key] != dict2[key]:
    #                 count +=1
    #                 print("values are not equal")
    #         else: print("some key is missing in dict")
        
    #     # Если все ключи и их значения одинаковы
    #     return count
    # @staticmethod 
    # def compare_dicts_by_values_spec_keys(dict1: dict, dict2: dict, array_of_keys: list):
    #     """Сравнивает два словаря по значениям в одинаковых ключах."""
        
    #     for key in dict1:
    #         if key in dict2:
    #             if key in array_of_keys:
    #                 if dict1[key] != dict2[key]:
    #                     print("values are not equal")
    #                     return False  # Если значения не совпадают, возвращаем False
    #         else: print("some key is missing in dict2")

    #     # Если все ключи и их значения одинаковы
    #     return True
    
    # @staticmethod
    # def compare_dicts_by_key(dict1, dict2, key, error_code):

    #     # Проверяем, существует ли ключ в обоих словарях
    #     if key in dict1 and key in dict2:
    #         if dict1[key] == dict2[key]:
    #             return 0  # Все хорошо, значения совпадают
    #         else:
    #             # print (message)
    #             return error_code  # Значения не совпадают
    #     else:
    #         return error_code 
    
    # #готово
    # @staticmethod
    # def compare_arrays_objects(array1: dict, array_et: dict):
    #     """Сравнивает два массива объектов на равенство."""
        # check =[0]*len(array_et)
        # count = 0
        # info = []

        # if len(array1) == len(array_et):
        #     for j in range (len(array_et)):
        #         check[j] =  array_et[j]
        #         for i in range(len(array1)):
        #             if array1[i] == array_et[j]:
        #                 check[j] = None
        #         if check[j]!= None:
        #             count+=1
        #             info.append(array_et[j])

        # if count == len(array_et):
        #     return ComparisonResult.__init__(True, len(array_et) - sum(check), None)
        # else:
        #     return ComparisonResult.__init__(False, len(array_et) - sum(check), info)

    
# class KBComparison():

#     mistakes_array: dict = None
    
#     # mistakes_dict = {
#     #     'mistake' = {
#     #         'kind' : [
#     #             data_kind = {
#     #                 'code' : str,
#     #                 'description' : str,
#     #             }
#     #         ],
#     #         'placement' : [
#     #             data_placement = {
#     #                 'code' : str,
#     #                 'Entity_kind': str,
#     #                 'Entity_Name': str,
#     #                 'Entity_parameter': str,
#     #             }
#     #         ],
#     #         'detalisation' : str,
#     #     }
#     # }
#     # здесь необходимо импортировать словарь, описывающий типологию ошибок и их описание
#     def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
#         super().__init__(connection_parameters, *args, **kwargs)
        
#         self.skills = {} # временное хранилище, тут лучше подключить БД или что-то
#         self.cash = {}
#     @staticmethod
#     async def compare_types(type_dict: dict, task_id):
#         ''' сравнивание типов'''

#         # Получаем задачу с определенным id
#         try:
#             task = Task.objects.get(id=task_id)
#         except Task.DoesNotExist:
#             print(f"Задача с id {task_id} не найдена.")
#             return -1  # Возвращаем -1, если задача не найдена

#         # Доступ к полю event_params (JSON)
#         event_params = task.event_params
#         try:
#             event_params_dict = json.loads(event_params) if event_params else {}
#         except json.JSONDecodeError:
#             print(f"Ошибка при декодировании JSON для задачи с id {task_id}.")
#             return -2  # Возвращаем -2, если произошла ошибка декодирования JSON


#         fine = [0]*10
#         # Сравниваем по ключу 'id'
#         if 'id' in event_params_dict and 'id' in type_dict:
#             fine[0] = Comparison.compare_dicts_by_key(event_params_dict, type_dict, 'id', 2)
#         else:
#             print("Отсутствует ключ 'id' в одном из словарей.")


#         # Сравниваем по ключу 'meta'
#         if 'meta' in event_params_dict and 'meta' in type_dict:
#             fine[1] = Comparison.compare_dicts_by_key(event_params_dict, type_dict, 'meta', 2)
#         else:
#             print("Отсутствует ключ 'meta' в одном из словарей.")


#         if fine[1] == 0:
#             if type_dict['meta'] == "string":
#                 for item in type_dict['values']:
#                     if item['data'] in event_params_dict['values']:
#                         fine[2] += 0
#                     else:
#                         fine[2] -= 1
#             if type_dict['meta'] == "number":
#                 if type_dict['from'] != event_params_dict['from']:
#                     fine[3] -= 1
#                 if type_dict['to'] != event_params_dict['to']:
#                     fine[4] -= 1

#             # лажа но пока пусть так
#             if type_dict['meta'] == "fuzzy":
#                 if type_dict['membership_functions']!= event_params_dict['membership_functions']:
#                     fine[5] -= 1
                
#         total_fine = sum(fine)
#         return total_fine


#     @staticmethod
#     async def compare_objects(object_dict: dict, task_id):
#         """Сравнивает два словаря с учетом поля 'properties', проверяя их с точностью до перестановки элементов"""
        

#         # Получаем задачу с определенным id
#         try:
#             task = Task.objects.get(id=task_id)
#         except Task.DoesNotExist:
#             print(f"Задача с id {task_id} не найдена.")
#             return -1  # Возвращаем -1, если задача не найдена

#         # Доступ к полю event_params (JSON)
#         event_params = task.event_params
#         try:
#             event_params_dict = json.loads(event_params) if event_params else {}
#         except json.JSONDecodeError:
#             print(f"Ошибка при декодировании JSON для задачи с id {task_id}.")
#             return -2  # Возвращаем -2, если произошла ошибка декодирования JSON


#         # Сравниваем основные ключи
#         if object_dict.get('id') != event_params_dict.get('id'):
#             print(f"Различие по ключу 'id': {object_dict.get('id')} != {event_params_dict.get('id')}")
#             return False
        
#         if object_dict.get('group') != event_params_dict.get('group'):
#             print(f"Различие по ключу 'group': {object_dict.get('group')} != {event_params_dict.get('group')}")
#             return False

#         # Сравниваем 'properties' с точностью до перестановки
#         if 'properties' in object_dict and 'properties' in event_params_dict:
#             # Получаем список элементов из 'properties' (предполагаем, что это список словарей)
#             properties1 = object_dict['properties']
#             properties2 = event_params_dict['properties']
            
#             # Сортируем элементы по 'id' для гарантии одинакового порядка
#             properties1_sorted = sorted(properties1, key=lambda x: x['id'])
#             properties2_sorted = sorted(properties2, key=lambda x: x['id'])

#             # Проверяем, что количество элементов совпадает
#             if len(properties1_sorted) != len(properties2_sorted):
#                 print("Количество элементов в 'properties' различается.")
#                 # return False
            
#             # Проверяем элементы по ключам 'id' и 'type'
#             # тоже лажа но пока допустим так
#             for p1, p2 in zip(properties1_sorted, properties2_sorted):
#                 if p1['id'] != p2['id']:
#                     print(f"Различие по ключу 'id': {p1['id']} != {p2['id']}")
#                     return False
#                 if p1['type'] != p2['type']:
#                     print(f"Различие по ключу 'type': {p1['type']} != {p2['type']}")
#                     return False

#         else:
#             print("'properties' отсутствует в одном из словарей.")
#             return False

#         return True  # Если все проверки прошли, словари одинаковы

#     @staticmethod
#     async def compare_formulas(str1: str, str2: str):
#         print("от него мы получили больше ... чем информации")



#     async def compare_events(object_dict: dict, task_id):
#         # Получаем задачу с определенным id
#         try:
#             task = Task.objects.get(id=task_id)
#         except Task.DoesNotExist:
#             print(f"Задача с id {task_id} не найдена.")
#             return -1  # Возвращаем -1, если задача не найдена

#         # Доступ к полю event_params (JSON)
#         event_params = task.event_params
#         try:
#             event_params_dict = json.loads(event_params) if event_params else {}
#         except json.JSONDecodeError:
#             print(f"Ошибка при декодировании JSON для задачи с id {task_id}.")
#             return -2  # Возвращаем -2, если произошла ошибка декодирования JSON
        

#         # Сравниваем основные ключи
#         if object_dict.get('Name') != event_params_dict.get('Name'):
#             print(f"Различие по ключу 'Name': {object_dict.get('Name')} != {event_params_dict.get('Name')}")
#             return False
#         fine = []

#         total_fine = sum(fine)
#         return total_fine


#     async def compare_intervals(object_dict: dict, task_id):
                

#         # Получаем задачу с определенным id
#         try:
#             task = Task.objects.get(id=task_id)
#         except Task.DoesNotExist:
#             print(f"Задача с id {task_id} не найдена.")
#             return -1  # Возвращаем -1, если задача не найдена

#         # Доступ к полю event_params (JSON)
#         event_params = task.event_params
#         try:
#             event_params_dict = json.loads(event_params) if event_params else {}
#         except json.JSONDecodeError:
#             print(f"Ошибка при декодировании JSON для задачи с id {task_id}.")
#             return -2  # Возвращаем -2, если произошла ошибка декодирования JSON
#         if object_dict.get('Name') != event_params_dict.get('Name'):
#             print(f"Различие по ключу 'Name': {object_dict.get('Name')} != {event_params_dict.get('Name')}")
#             return False
        
#         fine = []
#         fine[1] = KBComparison.compare_formulas(object_dict['Open'], event_params_dict['Open'])
#         fine[2] = KBComparison.compare_formulas(object_dict['Close'], event_params_dict['Close'])

#         total_fine = sum(fine)
#         return total_fine



#     async def compare_ruless(rule_dict: dict, task_id):

#         # Получаем задачу с определенным id
#         try:
#             task = Task.objects.get(id=task_id)
#         except Task.DoesNotExist:
#             print(f"Задача с id {task_id} не найдена.")
#             return -1  # Возвращаем -1, если задача не найдена

#         # Доступ к полю event_params (JSON)
#         event_params = task.event_params
#         try:
#             event_params_dict = json.loads(event_params) if event_params else {}
#         except json.JSONDecodeError:
#             print(f"Ошибка при декодировании JSON для задачи с id {task_id}.")
#             return -2  # Возвращаем -2, если произошла ошибка декодирования JSON
        
#         # Сравниваем основные ключи
#         if rule_dict.get('id') != event_params_dict.get('id'):
#             print(f"Различие по ключу 'id': {rule_dict.get('id')} != {event_params_dict.get('id')}")
#             return False


#         fine = []
#         fine[1] = KBComparison.compare_formulas(rule_dict['condition'], event_params_dict['condition']) 

#         total_fine = sum(fine)
#         return total_fine


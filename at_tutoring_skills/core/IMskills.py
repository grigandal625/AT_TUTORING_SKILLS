from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from .api_client import get_skill, get_skills, get_tasks, get_task, get_reaction, get_event
# далее делаешь импорт всех классов, спроси влада что именно нужно
# я не знаю про им

class ATTutoringKBSkills(ATComponent):


    skills: dict = None

    # .__dict__()
    kash = {
        'auth_token': None,
        'mark' : None,
        # ... описываешь что хранишь тут 
    }
    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        
        self.skills = {} # временное хранилище, тут лучше подключить БД или что-то
        
        
    # далее описываешь  вспомогательные методы get add cacl 
    # и тд из того, что тебе нужно
    # и методы описывающие реакции на события handleoperationcreated и тд
        

    # в статические методы не передается экземпляр класса
    # подходят для простой обработки без рабоы с kash
    @staticmethod
    def kb_event_from_dict(data: dict, event: str)-> dict:
        return 0

    # простые методы класса, если есть работа с kash делай их
    def get_operation_name_by_id(self, id: str):
        return 0
        
    # проверь название метода и замени, это просто шаблон
    @authorized_method
    async def handle_operation_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый опреацию: ', data)

        
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method


class ATTutoringSkills(ATComponent):
    
    skills: dict = None
    
    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        
        self.skills = {} # временное хранилище, тут лучше подключить БД или что-то
    
    @authorized_method
    async def handle_kb_type_created(self, event: str, data: dict, auth_token: str):
        print('Обучаемый создал пустой тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})
        
        current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        
        self.skills[auth_token] = current_skills
        
        if current_skills['kb_types'] >= 50:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    
    
    @authorized_method
    async def handle_kb_type_updated(self, event: str, data: dict, auth_token: str):
        print('Обучаемый отредактировал тип (БЗ): ', data)
        
        current_skills = self.skills.get(auth_token, {})
        
        current_skills['kb_types'] = self.calc_kb_type_skills(current_skills, data)
        
        # временная заглушка, что навыки набраны
        
        current_skills['kb_types'] = 60
        
        self.skills[auth_token] = current_skills
        
        if current_skills['kb_types'] >= 50:
            return {'skills': current_skills, 'stage_done': True}
        
        return {'skills': current_skills, 'stage_done': False, 'message': 'Обратите внимание на ошибки'}
    
    
    def calc_kb_type_skills(self, current_skills, data):
        
        # Подсчет скиллов для типов БЗ
        
        return 0
        
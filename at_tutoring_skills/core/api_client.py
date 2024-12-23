import requests

# Базовый URL для API
BASE_URL = "http://127.0.0.1:8000/skills_data/"

def get_skills():
    """Получить все навыки."""
    url = BASE_URL + "skills/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении навыков: {response.status_code}")
    
def get_skill(skil_id):
    """Получить навык по ID."""
    url = BASE_URL + f"skills/{skil_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении навыка с ID {skil_id}: {response.status_code}")
    
def get_tasks():
    """Получить все задачи."""
    url = BASE_URL + "tasks/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении задач: {response.status_code}")
    
def get_task(task_id):

    """Получить задачу по ID."""
    url = BASE_URL + f"tasks/{task_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении задачи с ID {task_id}: {response.status_code}")
    

def get_reaction(reaction_id):
    """Получить реакцию по ID."""
    url = BASE_URL + f"reactions/{reaction_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении реакции с ID {reaction_id}: {response.status_code}")
    
def get_event(event_id):
    """Получить событие по ID."""
    url = BASE_URL + f"events/{event_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        raise Exception(f"Ошибка при получении события с ID {event_id}: {response.status_code}")
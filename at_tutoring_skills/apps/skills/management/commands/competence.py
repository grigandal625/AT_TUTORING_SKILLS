import csv
from django.core.management.base import BaseCommand
from at_tutoring_skills.apps.skills.models import Skill, Competence, SkillCompetence


class Command(BaseCommand):
    help = 'Загружает связи между навыками и компетенциями из CSV файла в fixtures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', 
            type=str, 
            default='competence_skill',
            help='Имя CSV файла (без расширения) в папке fixtures'
        )

    def handle(self, *args, **options):
        file_name = "competence_skill"
        csv_file_path = f'at_tutoring_skills/apps/skills/management/commands/data_kb/{file_name}.csv'
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            
                csv_reader = csv.reader(csv_file)
                
                headers = next(csv_reader)
                
                skill_column = headers[0].strip() 
                self.stdout.write(f"Найдено навыков: {headers[0]}")

                competence_names = [h.strip() for h in headers[1:6]]  # Берем первые 5 компетенций
                
                self.stdout.write(f"Найдено компетенций: {competence_names}")
                
                # Получаем или создаем компетенции
                competences = {}
                for comp_name in competence_names:
                    competence, created = Competence.objects.get_or_create(
                        name=comp_name,
                        defaults={'code': comp_name}  
                    )
                    competences[comp_name] = competence
                    if created:
                        self.stdout.write(f"Создана новая компетенция: {comp_name}")
                
                # Обрабатываем строки с данными
                skills_processed = 0
                relations_created = 0
                relations_updated = 0
                
                for row in csv_reader:
                    if len(row) < 6:  # Проверяем, что есть все необходимые данные
                        self.stdout.write(self.style.WARNING(f"Пропущена строка: недостаточно данных {row}"))
                        continue
                    
                    skill_code = row[0].strip()
                    weights = []
                    
                    # Парсим веса для каждой компетенции (столбцы 1-5)
                    try:
                        weights = [int(row[i].strip()) if row[i].strip() else 0 for i in range(1, 6)]
                    except ValueError as e:
                        self.stdout.write(self.style.WARNING(
                            f"Ошибка преобразования весов для навыка {skill_code}: {e}"
                        ))
                        continue
                    
                    # Ищем навык по коду
                    try:
                        skill = Skill.objects.get(code=skill_code)
                    except Skill.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Навык с кодом {skill_code} не найден, пропускаем"
                        ))
                        continue
                    
                    # Создаем связи с компетенциями
                    for i, weight in enumerate(weights):
                        if weight > 0:  # Создаем связь только если вес больше 0
                            competence_name = competence_names[i]
                            competence = competences[competence_name]
                            
                            # Обновляем или создаем связь
                            relation, created = SkillCompetence.objects.update_or_create(
                                skill=skill,
                                competence=competence,
                                defaults={'weight': weight}
                            )
                            
                            if created:
                                relations_created += 1
                                self.stdout.write(
                                    f"Создана связь: {skill.code} -> {competence_name} (вес: {weight})"
                                )
                            else:
                                relations_updated += 1
                                self.stdout.write(
                                    f"Обновлена связь: {skill.code} -> {competence_name} (вес: {weight})"
                                )
                    
                    skills_processed += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f"\nОбработано навыков: {skills_processed}\n"
                    f"Создано связей: {relations_created}\n"
                    f"Обновлено связей: {relations_updated}"
                ))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f"Файл не найден: {csv_file_path}\n"
                f"Убедитесь, что файл существует в указанной директории"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при обработке файла: {e}"))
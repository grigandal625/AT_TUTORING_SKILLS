from graphviz import Digraph
from dto import Skill, SkillRelation, UserSkill

def build_skill_graph(skills: list[Skill], 
                     relations: list[SkillRelation],
                     user_skills: list[UserSkill]) -> Digraph:
    
    dot = Digraph(comment='Skills Graph', engine='dot')
    dot.attr(rankdir='TB', splines="spline", newrank='true')

    # Определяем корневые узлы (без входящих связей типа 1 или 2)
    has_incoming = set()
    for rel in relations:
        if rel.relation_type in {1, 2}:  # Иерархия или агрегация
            has_incoming.add(rel.target_skill_id)

    root_nodes = [str(s.pk) for s in skills if s.pk not in has_incoming]

    # Создаем невидимый subgraph для выравнивания корневых узлов
    with dot.subgraph(name='cluster_roots') as roots:
        roots.attr(rank='same')
        # Добавляем невидимые связи между корневыми узлами
        if len(root_nodes) > 1:
            roots.attr(ordering='out')
            for i in range(len(root_nodes)-1):
                roots.edge(root_nodes[i], root_nodes[i+1], style='invis', weight='100')

    # Определяем уровни для всех узлов
    skill_levels = {}
    current_level = 0
    current_level_nodes = root_nodes.copy()
    
    while current_level_nodes:
        next_level_nodes = []
        
        # Записываем уровень для текущих узлов
        for node in current_level_nodes:
            skill_levels[node] = current_level
        
        # Находим узлы следующего уровня (дочерние узлы через связи типа 1 или 2)
        for rel in relations:
            if rel.relation_type in {1, 2} and str(rel.source_skill_id) in current_level_nodes:
                target = str(rel.target_skill_id)
                if target not in skill_levels:  # Чтобы не перезаписывать уровни
                    next_level_nodes.append(target)
        
        current_level_nodes = list(set(next_level_nodes))  # Убираем дубликаты
        current_level += 1

    # Создаем невидимые подграфы для каждого уровня (кроме корневого)
    max_level = max(skill_levels.values(), default=0)
    for level in range(1, max_level + 1):
        level_nodes = [node for node, lvl in skill_levels.items() if lvl == level]
        if len(level_nodes) > 1:  # Выравниваем только если узлов больше одного
            with dot.subgraph(name=f'cluster_level_{level}') as sub:
                sub.attr(rank='same')
                sub.attr(ordering='out')
                for i in range(len(level_nodes)-1):
                    sub.edge(level_nodes[i], level_nodes[i+1], style='invis', weight='100')

    # Стили для различных типов связей
    relation_types = {
        1: ('Иерархия', 'black', 'solid'),
        2: ('Агрегация', 'blue', 'dashed'),
        3: ('Ассоциация', 'green', 'dotted'),
        4: ('Слабая', 'red', 'bold')
    }

    # Добавление узлов с визуальным выделением корневых
    user_marks = {us.skill_id: us.mark for us in user_skills}
    for skill in skills:
        mark = user_marks.get(skill.pk, 0.0)
        is_root = str(skill.pk) in root_nodes
        dot.node(
            str(skill.pk),
            label=f"SK-{skill.pk}\nОЦЕНКА: {mark:.1f}",
            shape='ellipse',
            style='filled',
            fillcolor='#a6d8ff' if is_root else 'lightgray',
            fontsize='10',
            fontname='Arial',
            penwidth='2.0' if is_root else '1.0'
        )

    # Добавление связей
    for rel in relations:
        label, color, style = relation_types.get(rel.relation_type, ('Неизвестно', 'grey', 'solid'))
        dot.edge(
            str(rel.source_skill_id),
            str(rel.target_skill_id),
            color=color,
            style=style,
            penwidth='1.5',
            arrowhead='normal',
            fontname='Arial'
        )

    # Генерация легенды
    # legend_content = _generate_legend_content(skills, user_marks, relation_types, root_nodes)
    # with dot.subgraph(name='cluster_legend') as legend:
    #     legend.attr(
    #         label='',
    #         labelloc='b',
    #         margin='50',
    #         style='filled',
    #         fillcolor='floralwhite',
    #         fontname='Arial'
    #     )
    #     legend.node('legend', label=legend_content, shape='none', fontsize='9')

    return dot

def build_legend_graph(skills: list[Skill], 
                     relations: list[SkillRelation],
                     user_skills: list[UserSkill]) -> Digraph:
    """Создает отдельный граф с легендой для дерева навыков."""
    
    dot = Digraph(comment='Skills Legend', engine='dot')
    dot.attr(rankdir='TB', margin="0.2", pad="0.5")
    
    # Определяем корневые узлы (без входящих связей типа 1 или 2)
    has_incoming = set()
    for rel in relations:
        if rel.relation_type in {1, 2}:  # Иерархия или агрегация
            has_incoming.add(rel.target_skill_id)

    root_nodes = [str(s.pk) for s in skills if s.pk not in has_incoming]
    
    # Стили для различных типов связей
    relation_types = {
        1: ('Иерархия', 'black', 'solid'),
        2: ('Агрегация', 'blue', 'dashed'),
        3: ('Ассоциация', 'green', 'dotted'),
        4: ('Слабая', 'red', 'bold')
    }
    
    user_marks = {us.skill_id: us.mark for us in user_skills}
    legend_content = _generate_legend_content(skills, user_marks, relation_types, root_nodes)
    
    dot.node(
        'legend', 
        label=legend_content, 
        shape='none', 
        fontsize='10',
        fontname='Arial'
    )
    
    return dot


def _generate_legend_content(skills: list[Skill], 
                            user_marks: dict[int, float],
                            relation_types: dict,
                            root_nodes: list[str]) -> str:
    """Генерирует HTML-контент для расширенной легенды."""
    legend = '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        <TR><TD COLSPAN="3"><B>ЛЕГЕНДА</B></TD></TR>
        
        <!-- Секция корневых узлов -->
        <TR><TD COLSPAN="3"><B>Корневые узлы</B></TD></TR>
        <TR><TD><B>ID</B></TD><TD><B>Навык</B></TD><TD><B>Оценка</B></TD></TR>'''
    
    # Сначала выводим корневые узлы
    for skill in skills:
        if str(skill.pk) in root_nodes:
            mark = user_marks.get(skill.pk, 0.0)
            legend += f'''
            <TR>
                <TD BGCOLOR="#a6d8ff">SK-{skill.pk}</TD>
                <TD BGCOLOR="#a6d8ff">{skill.name}</TD>
                <TD BGCOLOR="#a6d8ff">{mark:.1f}</TD>
            </TR>'''

    # Затем обычные узлы
    legend += '''
        <TR><TD COLSPAN="3"><B>Остальные узлы</B></TD></TR>'''
    for skill in skills:
        if str(skill.pk) not in root_nodes:
            mark = user_marks.get(skill.pk, 0.0)
            legend += f'''
            <TR>
                <TD>SK-{skill.pk}</TD>
                <TD>{skill.name}</TD>
                <TD>{mark:.1f}</TD>
            </TR>'''

    # Секция типов связей
    legend += '''
        <TR><TD COLSPAN="3"><B>Типы связей</B></TD></TR>
        <TR><TD><B>Тип</B></TD><TD><B>Описание</B></TD><TD><B>Пример</B></TD></TR>'''
    
    arrow_examples = {
        'solid': '─────▶',      # Сплошная линия
        'dashed': '─ ─ ─▶',     # Пунктир из обычных чёрточек
        'dotted': '·····▶',     # Точки
        'bold': '━━━━━▶'        # Жирная линия
    }

    for type_id, (name, color, style) in relation_types.items():
        legend += f'''
        <TR>
            <TD>{type_id}</TD>
            <TD>{name}</TD>
            <TD>
                <FONT COLOR="{color}">{arrow_examples[style]}</FONT>
            </TD>
        </TR>'''
    
    legend += '</TABLE>>'
    return legend

if __name__ == '__main__':
    skills = [
        # Основные технические навыки (группа 1)
        Skill(pk=1, name="Программирование", group=1, code=100),
        Skill(pk=2, name="Python", group=1, code=101),
        Skill(pk=3, name="Java", group=1, code=102),
        Skill(pk=4, name="Фреймворки Python", group=1, code=103),
        Skill(pk=5, name="Django", group=1, code=104),
        Skill(pk=6, name="Flask", group=1, code=105),
        Skill(pk=7, name="Асинхронное программирование", group=1, code=106),
        
        # Базы данных (группа 2)
        Skill(pk=8, name="Базы данных", group=2, code=200),
        Skill(pk=9, name="SQL", group=2, code=201),
        Skill(pk=10, name="PostgreSQL", group=2, code=202),
        Skill(pk=11, name="Оптимизация запросов", group=2, code=203),
        Skill(pk=12, name="NoSQL", group=2, code=204),
        Skill(pk=13, name="MongoDB", group=2, code=205),
        
        # DevOps (группа 3)
        Skill(pk=14, name="DevOps", group=3, code=300),
        Skill(pk=15, name="Docker", group=3, code=301),
        Skill(pk=16, name="Kubernetes", group=3, code=302),
        Skill(pk=17, name="CI/CD", group=3, code=303),
        
        # Мягкие навыки (группа 4)
        Skill(pk=18, name="Коммуникация", group=4, code=400),
        Skill(pk=19, name="Работа в команде", group=4, code=401),
        Skill(pk=20, name="Управление временем", group=4, code=402),
    ]

    relations = [
        # Иерархические связи (тип 1) - глубокая вложенность
        SkillRelation(pk=1, source_skill_id=1, target_skill_id=2, relation_type=1),  # Программирование → Python
        SkillRelation(pk=2, source_skill_id=1, target_skill_id=3, relation_type=1),  # Программирование → Java
        SkillRelation(pk=3, source_skill_id=2, target_skill_id=4, relation_type=1),  # Python → Фреймворки Python
        SkillRelation(pk=4, source_skill_id=4, target_skill_id=5, relation_type=1),  # Фреймворки → Django
        SkillRelation(pk=5, source_skill_id=4, target_skill_id=6, relation_type=1),  # Фреймворки → Flask
        SkillRelation(pk=6, source_skill_id=2, target_skill_id=7, relation_type=1),  # Python → Асинхронное программирование
        
        SkillRelation(pk=7, source_skill_id=8, target_skill_id=9, relation_type=1),  # БД → SQL
        SkillRelation(pk=8, source_skill_id=9, target_skill_id=10, relation_type=1),  # SQL → PostgreSQL
        SkillRelation(pk=9, source_skill_id=9, target_skill_id=11, relation_type=1),  # SQL → Оптимизация
        SkillRelation(pk=10, source_skill_id=8, target_skill_id=12, relation_type=1), # БД → NoSQL
        SkillRelation(pk=11, source_skill_id=12, target_skill_id=13, relation_type=1),# NoSQL → MongoDB
        
        SkillRelation(pk=12, source_skill_id=14, target_skill_id=15, relation_type=1), # DevOps → Docker
        SkillRelation(pk=13, source_skill_id=14, target_skill_id=16, relation_type=1), # DevOps → Kubernetes
        SkillRelation(pk=14, source_skill_id=14, target_skill_id=17, relation_type=1), # DevOps → CI/CD
        
        # Агрегации (тип 2) - на разных уровнях
        SkillRelation(pk=15, source_skill_id=18, target_skill_id=19, relation_type=2), # Коммуникация → Работа в команде
        SkillRelation(pk=16, source_skill_id=18, target_skill_id=20, relation_type=2),  # Коммуникация → Управление временем
        
        # Ассоциации (тип 3) - разноуровневые
        SkillRelation(pk=17, source_skill_id=2, target_skill_id=8, relation_type=3),   # Python ↔ БД
        SkillRelation(pk=18, source_skill_id=5, target_skill_id=10, relation_type=3),  # Django ↔ PostgreSQL
        SkillRelation(pk=19, source_skill_id=7, target_skill_id=16, relation_type=3),  # Асинхронное ↔ Kubernetes
        SkillRelation(pk=20, source_skill_id=11, target_skill_id=17, relation_type=3), # Оптимизация ↔ CI/CD
        
        # Слабые связи (тип 4) - кросс-уровневые
        SkillRelation(pk=21, source_skill_id=19, target_skill_id=14, relation_type=4), # Работа в команде ⇢ DevOps
        SkillRelation(pk=22, source_skill_id=20, target_skill_id=1, relation_type=4),  # Управление временем ⇢ Программирование
        SkillRelation(pk=23, source_skill_id=13, target_skill_id=7, relation_type=4),  # MongoDB ⇢ Асинхронное
        SkillRelation(pk=24, source_skill_id=6, target_skill_id=12, relation_type=4),  # Flask ⇢ NoSQL

        # Слабые связи для одинаковых уровней
        SkillRelation(pk=25, source_skill_id=6, target_skill_id=17, relation_type=4),
        SkillRelation(pk=26, source_skill_id=9, target_skill_id=19, relation_type=4),
        
    ]

    user_skills = [
        UserSkill(pk=1, user_id=1, skill_id=1, mark=4.5),
        UserSkill(pk=2, user_id=1, skill_id=2, mark=4.7),
        UserSkill(pk=3, user_id=1, skill_id=3, mark=3.8),
        UserSkill(pk=4, user_id=1, skill_id=4, mark=4.2),
        UserSkill(pk=5, user_id=1, skill_id=5, mark=4.0),
        UserSkill(pk=6, user_id=1, skill_id=6, mark=3.9),
        UserSkill(pk=7, user_id=1, skill_id=7, mark=4.1),
        UserSkill(pk=8, user_id=1, skill_id=8, mark=4.3),
        UserSkill(pk=9, user_id=1, skill_id=9, mark=4.4),
        UserSkill(pk=10, user_id=1, skill_id=10, mark=4.2),
        UserSkill(pk=11, user_id=1, skill_id=11, mark=3.9),
        UserSkill(pk=12, user_id=1, skill_id=12, mark=4.0),
        UserSkill(pk=13, user_id=1, skill_id=13, mark=3.8),
        UserSkill(pk=14, user_id=1, skill_id=14, mark=3.7),
        UserSkill(pk=15, user_id=1, skill_id=15, mark=4.1),
        UserSkill(pk=16, user_id=1, skill_id=16, mark=3.5),
        UserSkill(pk=17, user_id=1, skill_id=17, mark=3.9),
        UserSkill(pk=18, user_id=1, skill_id=18, mark=4.5),
        UserSkill(pk=19, user_id=1, skill_id=19, mark=4.3),
        UserSkill(pk=20, user_id=1, skill_id=20, mark=4.0),
    ]

    # Генерация и сохранение графа
    graph = build_skill_graph(skills, relations, user_skills)
    graph.format = 'png'
    graph.render('skills_graph', view=True, cleanup=True)

    legend_graph = build_legend_graph(skills, relations, user_skills)
    legend_graph.format = 'png'
    legend_graph.render('skills_legend', view=True, cleanup=True)

from dataclasses import dataclass


@dataclass(kw_only=True)
class Skill:
    pk: int
    name: str
    group: int
    code: int


@dataclass(kw_only=True)
class SkillRelation:
    pk: int
    source_skill_id: int
    target_skill_id: int
    relation_type: int # 1 - hierarchy, 2 - aggregation, 3 - association, 4 - week


@dataclass(kw_only=True)
class UserSkill:
    pk: int
    user_id: str | int
    skill_id: int
    mark: float

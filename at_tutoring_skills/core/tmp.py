import asyncio  # для запуска main

from data_serializers import KBClassDataSerializer
from data_serializers import KBEventDataSerializer
from data_serializers import KBIntervalDataSerializer
from data_serializers import KBRuleDataSerializer
from data_serializers import KBTypeDataSerializer


async def main():
    # примеры данных, поступающих в событии
    symbolic_type_data = {
        "id": 1,
        "kt_values": [{"data": "Сухой"}, {"data": "Влажный"}, {"data": "Отсутствует"}],
        "kb_id": "КАШЕЛЬ",
        "meta": 1,
        "comment": None,
    }

    numeric_type_data = {
        "id": 2,
        "kt_values": [{"data": 3}, {"data": 42}],
        "kb_id": "ТЕМПЕРАТУРА",
        "meta": 2,
        "comment": None,
    }

    fuzzy_type_data = {
        "id": 3,
        "kt_values": [
            {
                "data": {
                    "tag": "parameter",
                    "points": [
                        {"tag": "point", "x": 50, "y": 0},
                        {"tag": "point", "x": 110, "y": 0.3},
                        {"tag": "point", "x": 150, "y": 1},
                        {"tag": "point", "x": 170, "y": 1},
                    ],
                    "name": "Высокое",
                    "min": 50,
                    "max": 170,
                }
            },
            {
                "data": {
                    "tag": "parameter",
                    "points": [
                        {"tag": "point", "x": 50, "y": 1},
                        {"tag": "point", "x": 70, "y": 1},
                        {"tag": "point", "x": 110, "y": 0},
                        {"tag": "point", "x": 170, "y": 0},
                    ],
                    "name": "Низкое",
                    "min": 50,
                    "max": 170,
                }
            },
        ],
        "kb_id": "ДАВЛЕНИЕ",
        "meta": 3,
        "comment": None,
    }

    symbolic_type_2_data = {
        "id": 4,
        "kt_values": [{"data": "Госпитализация"}, {"data": "Постельный режим"}, {"data": "Реанимация"}],
        "kb_id": "ДЕЙСТВИЯ",
        "meta": 1,
        "comment": None,
    }

    object_data = {
        "id": 1,
        "ko_attributes": [
            {"kb_id": "Температура", "comment": None, "type": 2},
            {"kb_id": "Давление", "comment": None, "type": 3},
            {"kb_id": "Кашель", "comment": None, "type": 1},
            {"kb_id": "Действия", "comment": None, "type": 4},
        ],
        "kb_id": "ПАЦИЕНТ",
        "group": "ГРУППА1",
        "comment": "ПАЦИЕНТ",
    }

    event_data = {
        "id": 1,
        "kb_id": "КРИТИЧЕСКОЕ_ДАВЛЕНИЕ",
        "occurance_condition": {
            "tag": "gt",
            "sign": "gt",
            "left": {"tag": "ref", "id": "ПАЦИЕНТ", "ref": {"id": "Давление", "tag": "ref"}},
            "right": {"tag": "value", "content": 140},
        },
        "comment": None,
    }

    interval_data = {
        "id": 2,
        "kb_id": "ВЫСОКАЯ_ТЕМПЕРАТУРА",
        "open": {
            "tag": "gt",
            "sign": "gt",
            "left": {"tag": "ref", "id": "ПАЦИЕНТ", "ref": {"id": "Температура", "tag": "ref"}},
            "right": {"tag": "value", "content": 37.5},
        },
        "close": {
            "tag": "le",
            "sign": "le",
            "left": {"tag": "ref", "id": "ПАЦИЕНТ", "ref": {"id": "Температура", "tag": "ref"}},
            "right": {"tag": "value", "content": 37.5},
        },
        "comment": None,
    }

    rule_data = {
        "id": 2,
        "kr_instructions": [
            {
                "id": 9,
                "data": {
                    "ref": {"tag": "ref", "id": "ПАЦИЕНТ", "ref": {"id": "Действия", "tag": "ref"}},
                    "value": {"tag": "value", "content": "Реанимация"},
                },
            }
        ],
        "kr_else_instructions": [],
        "kb_id": "ПРАВИЛО1",
        "condition": {
            "tag": "and",
            "sign": "and",
            "left": {
                "tag": "d",
                "left": {"tag": "ref", "id": "КРИТИЧЕСКОЕ_ДАВЛЕНИЕ", "meta": "allen_reference"},
                "right": {"tag": "ref", "id": "ВЫСОКАЯ_ТЕМПЕРАТУРА", "meta": "allen_reference"},
            },
            "right": {
                "tag": "eq",
                "sign": "eq",
                "left": {"tag": "ref", "id": "ПАЦИЕНТ", "ref": {"id": "Кашель", "tag": "ref"}},
                "right": {"tag": "value", "content": "Сухой"},
            },
        },
        "comment": None,
    }

    # кэш типов в виде int: KBType, может быть другой в зависимости от твоего кеша
    types = {}

    # функция, достающая тип по числовомо id, может быть другой в зависимости от твоего кеша
    async def get_type_by_id(type_id):
        return types.get(type_id)

    # применение сериализаторов

    serializer = KBTypeDataSerializer(data=symbolic_type_data)
    result = await serializer.asave()
    print(result.krl)
    types[symbolic_type_data["id"]] = result  # запоминаем тип в кэше

    serializer = KBTypeDataSerializer(data=numeric_type_data)
    result = await serializer.asave()
    print(result.krl)
    types[numeric_type_data["id"]] = result  # запоминаем тип в кэше

    serializer = KBTypeDataSerializer(data=fuzzy_type_data)
    result = await serializer.asave()
    print(result.krl)
    types[fuzzy_type_data["id"]] = result  # запоминаем тип в кэше

    serializer = KBTypeDataSerializer(data=symbolic_type_2_data)
    result = await serializer.asave()
    print(result.krl)
    types[symbolic_type_2_data["id"]] = result  # запоминаем тип в кэше

    serializer = KBClassDataSerializer(
        data=object_data, context={"type_by_id_getter": get_type_by_id}
    )  # передаем функцию для получения типа по числовому id чтоб определить имена типов атрибутов
    result = await serializer.asave()
    print(result.krl)

    serializer = KBEventDataSerializer(data=event_data)
    result = await serializer.asave()
    print(result.krl)

    serializer = KBIntervalDataSerializer(data=interval_data)
    result = await serializer.asave()
    print(result.krl)

    serializer = KBRuleDataSerializer(data=rule_data)
    result = await serializer.asave()
    print(result.krl)


if __name__ == "__main__":
    import os

    if not os.getenv("DJANGO_SETTINGS_MODULE", None):
        from django.conf import settings
        import django

        settings.configure(INSTALLED_APPS=["rest_framework", "adrf"], DEBUG=True)
        django.setup()

    asyncio.run(main())

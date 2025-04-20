import inspect
from typing import Awaitable
from typing import Callable
from typing import Union

from adrf import fields
from adrf import serializers
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from at_krl.core.kb_type import KBType
from at_krl.models.kb_class import KBClassModel
from at_krl.models.kb_operation import AllenAttributeExpressionModel
from at_krl.models.kb_operation import AllenOperationModel
from at_krl.models.kb_operation import KBOperationModel
from at_krl.models.kb_operation import KBReferenceModel
from at_krl.models.kb_operation import KBValueModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.models.kb_type import KBFuzzyTypeModel
from at_krl.models.kb_type import KBNumericTypeModel
from at_krl.models.kb_type import KBSymbolicTypeModel
from at_krl.models.simple.simple_operation import SimpleOperationModel
from at_krl.models.simple.simple_operation import SimpleReferenceModel
from at_krl.models.simple.simple_operation import SimpleValueModel
from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.utils.context import Context
from pydantic import RootModel
from pydantic import ValidationError
from rest_framework import exceptions


class FieldMappedSerializer(serializers.Serializer):
    field_name_map = {}

    def _map_keys(self, data):
        return {self.field_name_map.get(key, key): value for key, value in data.items()}

    def to_representation(self, instance):
        res = super().to_representation(instance)
        return self._map_keys(res)

    async def ato_representation(self, instance):
        res = await super().ato_representation(instance)
        return self._map_keys(res)


class Equals:
    check = None

    def __init__(self, check):
        self.check = check

    def __call__(self, value):
        if value != self.check:
            raise exceptions.ValidationError(detail=f"Value must be equal to {self.check}")


class SymbolicDataValueSerializer(serializers.Serializer):
    data = serializers.CharField()


class KBSymbolicTypeDataSerializer(FieldMappedSerializer):
    field_name_map = {"meta_out": "meta"}

    kt_values = serializers.ListField(child=SymbolicDataValueSerializer(), write_only=True, min_length=2)
    kb_id = serializers.CharField(write_only=True)
    meta = serializers.IntegerField(write_only=True, min_value=1, max_value=1)
    comment = serializers.CharField(allow_null=True, write_only=True)

    tag = serializers.CharField(read_only=True, default="type", validators=[Equals("type")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")
    meta_out = serializers.CharField(read_only=True, default="string", validators=[Equals("string")])
    values = fields.SerializerMethodField(read_only=True)

    def get_values(self, obj):
        return [item["data"] for item in obj["kt_values"]]

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBSymbolicTypeModel(**data)
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())
        return model.to_internal(Context(name="serializer"))

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBSymbolicTypeModel(**data)
            return model.to_internal(Context(name="serializer"))
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class NumericDataValueSerializer(serializers.Serializer):
    data = serializers.FloatField()


class KBNumericTypeDataSerializer(FieldMappedSerializer):
    field_name_map = {
        "meta_out": "meta",
        "from_": "from",
        "to_": "to",
    }

    kt_values = serializers.ListField(
        child=NumericDataValueSerializer(),
        write_only=True,
        min_length=2,
        max_length=2,
    )
    kb_id = serializers.CharField(write_only=True)
    meta = serializers.IntegerField(write_only=True, min_value=2, max_value=2)
    comment = serializers.CharField(allow_null=True, write_only=True)

    tag = serializers.CharField(read_only=True, default="type", validators=[Equals("type")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")
    meta_out = serializers.CharField(read_only=True, default="number", validators=[Equals("number")])
    from_ = fields.SerializerMethodField(read_only=True)
    to_ = fields.SerializerMethodField(read_only=True)

    def get_from_(self, obj):
        try:
            return obj["kt_values"][0]["data"]
        except Exception as e:
            raise exceptions.ValidationError(str(e))

    def get_to_(self, obj):
        try:
            return obj["kt_values"][1]["data"]
        except Exception as e:
            raise exceptions.ValidationError(str(e))

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBNumericTypeModel(**data)
            return model.to_internal(Context(name="serializer"))
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBNumericTypeModel(**data)
            return model.to_internal(Context(name="serializer"))
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class MFPointDataSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    tag = serializers.CharField(validators=[Equals("point")])


class MembershipFunctionDataSerializer(serializers.Serializer):
    points = serializers.ListField(
        child=MFPointDataSerializer(),
        write_only=True,
        min_length=2,
    )
    name = serializers.CharField()
    min = serializers.FloatField()
    max = serializers.FloatField()
    tag = serializers.CharField(validators=[Equals("parameter")])


class FuzzyDataValueSerializer(serializers.Serializer):
    data = MembershipFunctionDataSerializer()


class KBFuzzyTypeDataSerializer(FieldMappedSerializer):
    field_name_map = {
        "meta_out": "meta",
    }

    kt_values = serializers.ListField(child=FuzzyDataValueSerializer(), write_only=True, min_length=2)
    kb_id = serializers.CharField(write_only=True)
    meta = serializers.IntegerField(write_only=True, min_value=3, max_value=3)
    comment = serializers.CharField(allow_null=True, write_only=True)

    tag = serializers.CharField(read_only=True, default="type", validators=[Equals("type")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")
    meta_out = serializers.CharField(read_only=True, default="fuzzy", validators=[Equals("fuzzy")])
    membership_functions = fields.SerializerMethodField(read_only=True)

    def get_membership_functions(self, obj):
        return [item["data"] for item in obj["kt_values"]]

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBFuzzyTypeModel(**data)
            return model.to_internal(Context(name="serializer"))
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBFuzzyTypeModel(**data)
            return model.to_internal(Context(name="serializer"))
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class KBTypeDataSerializer(FieldMappedSerializer):
    meta = serializers.IntegerField(write_only=True, min_value=1, max_value=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_serializer = None

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        meta = result.get("meta")
        serializer_map = {1: KBSymbolicTypeDataSerializer, 2: KBNumericTypeDataSerializer, 3: KBFuzzyTypeDataSerializer}
        serializer = serializer_map[meta](data=data)
        self.child_serializer = serializer
        return serializer.to_internal_value(data)

    async def ato_internal_value(self, data):
        result = await super().ato_internal_value(data)
        meta = result.get("meta")
        serializer_map = {1: KBSymbolicTypeDataSerializer, 2: KBNumericTypeDataSerializer, 3: KBFuzzyTypeDataSerializer}
        serializer = serializer_map[meta](data=data)
        self.child_serializer = serializer
        return await serializer.ato_internal_value(data)

    def to_representation(self, instance):
        meta = instance.get("meta")
        serializer_map = {1: KBSymbolicTypeDataSerializer, 2: KBNumericTypeDataSerializer, 3: KBFuzzyTypeDataSerializer}

        serializer = serializer_map[meta](instance=instance)
        self.child_serializer = serializer
        return serializer.to_representation(instance)

    async def ato_representation(self, instance):
        meta = instance.get("meta")
        serializer_map = {1: KBSymbolicTypeDataSerializer, 2: KBNumericTypeDataSerializer, 3: KBFuzzyTypeDataSerializer}

        serializer = serializer_map[meta](instance=instance)
        self.child_serializer = serializer
        return await serializer.ato_representation(instance)

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        if not self.child_serializer:
            raise RuntimeError("Serializer not validated")
        return self.child_serializer.save(**kwargs)

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        if not self.child_serializer:
            raise RuntimeError("Serializer not validated")
        return await self.child_serializer.asave(**kwargs)


class KOAttributeSerializer(FieldMappedSerializer):
    kb_id = serializers.CharField(write_only=True)
    comment = serializers.CharField(allow_null=True, write_only=True)
    type = serializers.IntegerField()

    tag = serializers.CharField(read_only=True, default="property", validators=[Equals("property")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        type_by_id_getter: Callable[[int], KBType] | Awaitable = self.context.get("type_by_id_getter")
        type_id = self.validated_data["type"]
        if not type_by_id_getter:
            raise RuntimeError(f"Expected type_by_id_getter in context to allow saving in {self.__class__.__name__}")
        if inspect.iscoroutinefunction(type_by_id_getter):
            kb_type = async_to_sync(type_by_id_getter)(type_id)
        else:
            kb_type = type_by_id_getter(type_id)

        if not kb_type:
            attr_id = data.get("id")
            raise exceptions.ValidationError(f"KBType for id={type_id} for attribute {attr_id} not found")
        if not isinstance(kb_type, KBType):
            raise TypeError(f"Expected type for id={type_id} to be of type KBType, got {type(kb_type).__name__}")

        data["type"] = {"id": kb_type.id, "tag": "ref", "meta": "type_or_class"}
        self.resolved_type = kb_type
        return data

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        type_by_id_getter: Callable[[int], KBType] | Awaitable = self.context.get("type_by_id_getter")
        type_id = self.validated_data["type"]
        if not type_by_id_getter:
            raise RuntimeError(f"Expected type_by_id_getter in context to allow saving in {self.__class__.__name__}")
        if inspect.iscoroutinefunction(type_by_id_getter):
            kb_type = await type_by_id_getter(type_id)
        else:
            kb_type = await sync_to_async(type_by_id_getter)(type_id)
        if not kb_type:
            attr_id = data.get("id")
            raise exceptions.ValidationError(f"KBType for id={type_id} for attribute {attr_id} not found")
        if not isinstance(kb_type, KBType):
            raise TypeError(f"Expected type for id={type_id} to be of type KBType, got {type(kb_type).__name__}")
        data["type"] = {"id": kb_type.id, "tag": "ref", "meta": "type_or_class"}
        self.resolved_type = kb_type
        return data


class KBClassDataSerializer(FieldMappedSerializer):
    ko_attributes = KOAttributeSerializer(many=True, write_only=True)
    kb_id = serializers.CharField(write_only=True)
    comment = serializers.CharField(allow_null=True, write_only=True)

    tag = serializers.CharField(read_only=True, default="class", validators=[Equals("class")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")
    properties = fields.SerializerMethodField(read_only=True)

    async def get_properties(self, obj: dict):
        self.resolved_prop_types = {}
        result = []
        for attr in obj.get("ko_attributes"):
            type_by_id_getter: Callable[[int], KBType] | Awaitable = self.context["type_by_id_getter"]
            attr_serializer = KOAttributeSerializer(data=attr, context={"type_by_id_getter": type_by_id_getter})
            attr = await attr_serializer.asave()
            result.append(attr)
            self.resolved_prop_types[attr["id"]] = attr_serializer.resolved_type
        return result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "type_by_id_getter" not in self.context:
            raise RuntimeError(f"Expected type_by_id_getter provided in context to create {self.__class__.__name__}")

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBClassModel(**data)
            kb_class = model.to_internal(Context(name="serializer"))
            for property in kb_class.properties:
                attr_id = property.id
                property.type.target = self.resolved_prop_types[attr_id]
            return kb_class
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBClassModel(**data)
            kb_class = model.to_internal(Context(name="serializer"))
            for property in kb_class.properties:
                attr_id = property.id
                property.type.target = self.resolved_prop_types[attr_id]
            return kb_class
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class SimpleEvaluatableRootModel(RootModel[Union[SimpleOperationModel, SimpleReferenceModel, SimpleValueModel]]):
    def to_internal(self, context: Context):
        return self.root.to_internal(context)


def validate_simple_evaluatable(value: dict):
    try:
        SimpleEvaluatableRootModel(**value)
    except ValidationError as e:
        raise serializers.ValidationError(detail=e.errors())


class KBEventDataSerializer(serializers.Serializer):
    kb_id = serializers.CharField(write_only=True)
    comment = serializers.CharField(allow_null=True, write_only=True)

    occurance_condition = serializers.JSONField(validators=[validate_simple_evaluatable])

    tag = serializers.CharField(read_only=True, default="event", validators=[Equals("event")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBEventModel(**data)
            kb_event = model.to_internal(Context(name="serializer"))
            return kb_event
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBEventModel(**data)
            kb_event = model.to_internal(Context(name="serializer"))
            return kb_event
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class KBIntervalDataSerializer(serializers.Serializer):
    kb_id = serializers.CharField(write_only=True)
    comment = serializers.CharField(allow_null=True, write_only=True)

    open = serializers.JSONField(validators=[validate_simple_evaluatable])
    close = serializers.JSONField(validators=[validate_simple_evaluatable])

    tag = serializers.CharField(read_only=True, default="interval", validators=[Equals("interval")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBIntervalModel(**data)
            kb_interval = model.to_internal(Context(name="serializer"))
            return kb_interval
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBIntervalModel(**data)
            kb_interval = model.to_internal(Context(name="serializer"))
            return kb_interval
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())


class EvaluatableRootModel(
    RootModel[
        Union[KBValueModel, AllenAttributeExpressionModel, KBReferenceModel, KBOperationModel, AllenOperationModel]
    ]
):
    def to_internal(self, context: Context):
        return self.root.to_internal(context)


def validate_evaluatable(value: dict):
    try:
        EvaluatableRootModel(**value)
    except ValidationError as e:
        raise serializers.ValidationError(detail=e.errors())


def validate_kb_reference(value: dict):
    try:
        KBReferenceModel(**value)
    except ValidationError as e:
        raise serializers.ValidationError(detail=e.errors())


class InstructionDataValueSerializer(serializers.Serializer):
    ref = serializers.JSONField(validators=[validate_kb_reference])
    value = serializers.JSONField(validators=[validate_evaluatable])


class InstructionSerializer(serializers.Serializer):
    data = InstructionDataValueSerializer()


class KBRuleDataSerializer(serializers.Serializer):
    kb_id = serializers.CharField(write_only=True)
    comment = serializers.CharField(allow_null=True, write_only=True)
    kr_instructions = serializers.ListField(child=InstructionSerializer(), write_only=True, min_length=1)
    kr_else_instructions = serializers.ListField(
        child=InstructionSerializer(), write_only=True, allow_empty=True, allow_null=True, default=None
    )

    condition = serializers.JSONField(validators=[validate_evaluatable])

    tag = serializers.CharField(read_only=True, default="rule", validators=[Equals("rule")])
    id = serializers.CharField(read_only=True, source="kb_id")
    desc = serializers.CharField(read_only=True, source="comment")
    instructions = fields.SerializerMethodField(read_only=True)
    else_instructions = fields.SerializerMethodField(read_only=True)

    def get_instructions(self, obj):
        return [{"tag": "assign", **instruction["data"]} for instruction in obj["kr_instructions"]]

    def get_else_instructions(self, obj):
        if obj.get("kr_else_instructions"):
            return [{"tag": "assign", **instruction["data"]} for instruction in obj["kr_else_instructions"]]
        return []

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        self.instance = self.validated_data
        data = self.data
        try:
            model = KBRuleModel(**data)
            kb_rule = model.to_internal(Context(name="serializer"))
            return kb_rule
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

    async def asave(self, **kwargs):
        await self.ais_valid(raise_exception=True)
        self.instance = self.validated_data
        data = await self.adata
        try:
            model = KBRuleModel(**data)
            kb_rule = model.to_internal(Context(name="serializer"))
            return kb_rule
        except ValidationError as e:
            raise exceptions.ValidationError(detail=e.errors())

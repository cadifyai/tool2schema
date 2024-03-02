from __future__ import annotations

import typing
from enum import Enum
from inspect import Parameter, isclass
from typing import Literal, Optional, Type, Union

# Order matters: specific classes should appear before more generic ones,
# because the first matching schema will be used
TYPE_SCHEMAS: list[Type[TypeSchema]] = []


def GPTTypeSchema(cls: Type[TypeSchema]):
    """
    Decorator to register a type schema class.
    """
    cls.priority = len(TYPE_SCHEMAS)
    TYPE_SCHEMAS.insert(0, cls)  # Push to the front
    return cls


class TypeSchema:
    """
    Base class for type converters.
    """

    # Priority of this type schema (to be overridden by child classes),
    # the higher the priority, the more specific the type schema is;
    # schemas with higher priority will be checked first
    priority = -1

    def __init__(self, p_type: Optional[Type] = None):
        # The type can be none if the type was created manually, for example
        # via the add_enum method which creates an instance of EnumTypeSchema
        self.type = p_type

    @staticmethod
    def create(p_type: Type) -> Optional[TypeSchema]:
        """
        Create a new schema for the given type.

        :return: An instance of `TypeSchema`, or None if the type is not supported.
        """
        for schema in TYPE_SCHEMAS:
            if schema.matches(p_type):
                return schema(p_type)

    @staticmethod
    def matches(p_type: Type) -> bool:
        """
        Determine if this schema can be used for the given type.

        :return: True if this schema can be used to parse the given type
        """
        raise NotImplementedError()

    def encode(self, value):
        """
        Convert the given value to its JSON representation. Overriding methods should
        also override `decode` to convert the value back to its original type.

        :param value: The value to be converted
        :return: The JSON representation of the value
        """
        return value

    def decode(self, value):
        """
        Convert the given value from the JSON representation to an instance
        that can be passed to the original method as a parameter. Overriding
        methods should check whether the value needs to be converted, and return
        it as is if no conversion is necessary.

        :param value: The value to be converted
        :return: An instance of the type required by the original method
        """
        return value

    def _get_type(self) -> dict:
        """
        Get the type dictionary to be merged in the JSON schema.
        """
        return {}

    def _get_items(self) -> Union[dict, Parameter.empty]:
        """
        Get the items property to be added to the JSON schema.
        Return `Parameter.empty` to omit the items from the schema.
        """
        return Parameter.empty

    def _get_enum(self) -> Union[list, Parameter.empty]:
        """
        Get the enum property to be added to the JSON schema.
        Return `Parameter.empty` to omit the enum from the schema.
        """
        return Parameter.empty

    def to_json(self) -> dict:
        """
        Return the json schema for this type.
        """
        fields = {
            "items": self._get_items(),
            "enum": self._get_enum(),
            **self._get_type(),
        }

        return {f: v for f, v in fields.items() if v != Parameter.empty}


@GPTTypeSchema
class ValueTypeSchema(TypeSchema):
    """
    Type schema for value types.
    """

    TYPE_MAP = {
        "int": "integer",
        "float": "number",
        "str": "string",
        "bool": "boolean",
        "NoneType": "null",
    }

    @staticmethod
    def matches(p_type) -> bool:
        return True

    def _get_type(self) -> dict:
        return {"type": self.TYPE_MAP.get(self.type.__name__, "object")}


class GenericTypeSchema(TypeSchema):
    """
    Base class for generic types supporting subscription.
    """

    def _get_sub_types(self) -> list[TypeSchema]:
        """
        :return: A list of type schemas corresponding to the generic type arguments.
        """
        return [TypeSchema.create(arg) for arg in typing.get_args(self.type)]

    def _get_sub_type(self) -> Optional[TypeSchema]:
        """
        :return: A type schema corresponding to the single generic type argument,
            or None if there is none. If there are multiple arguments, the first
            one is returned.
        """
        if args := self._get_sub_types():
            return args[0]


@GPTTypeSchema
class ListTypeSchema(GenericTypeSchema):
    """
    Type schema for list (array) types, including typing.List.
    """

    @staticmethod
    def matches(p_type: Type) -> bool:
        return p_type != Parameter.empty and (p_type is list or typing.get_origin(p_type) is list)

    def _get_type(self) -> dict:
        return {"type": "array"}

    def _get_items(self) -> Union[dict, Parameter.empty]:
        if sub_type := self._get_sub_type():
            return sub_type.to_json()

        return Parameter.empty

    def encode(self, value):
        if sub_type := self._get_sub_type():
            return [sub_type.encode(v) for v in value]

        return value

    def decode(self, value):
        if sub_type := self._get_sub_type():
            return [sub_type.decode(v) for v in value]

        return value


@GPTTypeSchema
class UnionTypeSchema(GenericTypeSchema):
    """
    Type schema for typing.Optional types.
    """

    @staticmethod
    def matches(p_type: Type) -> bool:
        return p_type != Parameter.empty and typing.get_origin(p_type) is Union

    def _get_type(self) -> dict:
        return {"anyOf": [t.to_json() for t in self._get_sub_types()]}

    def _sorted_sub_types(self):
        """
        :return: Subtypes sorted by priority.
        """
        return sorted(self._get_sub_types(), key=lambda t: t.priority, reverse=True)

    def encode(self, value):
        # Delegate encoding to the first matching subtype
        for sub_type in self._sorted_sub_types():
            if sub_type.matches(type(value)):
                return sub_type.encode(value)

        return value

    def decode(self, value):
        # We have no way to know which type to decode to, so we try all of them
        # (ordered by priority) and return at the first one that produces a different value.
        for sub_type in self._sorted_sub_types():
            if (dec := sub_type.decode(value)) != value:
                return dec

        return value


class EnumTypeSchema(TypeSchema):
    """
    Base type schema form enumeration types.
    """

    def __init__(self, enum_values, type: Optional[Type] = None):
        super().__init__(type)
        self.enum_values = enum_values

    def _get_type(self) -> dict:
        return TypeSchema.create(type(self.enum_values[0]))._get_type()

    def _get_enum(self) -> Union[list, Parameter.empty]:
        return self.enum_values


@GPTTypeSchema
class EnumClassTypeSchema(EnumTypeSchema):
    """
    Type schema for enum.Enum types.
    """

    def __init__(self, p_type: Enum):
        super().__init__([e.name for e in p_type], p_type)

    @staticmethod
    def matches(type_p: Type) -> bool:
        return type_p != Parameter.empty and isclass(type_p) and issubclass(type_p, Enum)

    def encode(self, value):
        """
        Convert an enum instance to its name.

        :param value: The enum instance to be converted.
        """
        return value.name if isinstance(value, Enum) else value

    def decode(self, value):
        """
        Convert an enum name to an instance of the enum type.

        :param value: The enum name to be converted
        """
        if value in self.enum_values:
            # Convert to an enum instance
            return self.type[value]

        # The user is invoking the method directly passing the enum instance
        return value


@GPTTypeSchema
class LiteralTypeSchema(EnumTypeSchema):
    """
    Type schema for typing.Literal types.
    """

    def __init__(self, p_type):
        values = list(typing.get_args(p_type))
        super().__init__(values, p_type)

    @staticmethod
    def matches(p_type: Type) -> bool:
        return p_type != Parameter.empty and typing.get_origin(p_type) is Literal

import re
import typing
from enum import Enum
from inspect import Parameter, isclass
from typing import Union

TYPE_MAP = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean",
    "list": "array",
}


class ParameterSchema:
    """
    Automatically create a parameter schema given an instance of
    inspect.Parameter and a function documentation string.
    """

    def __init__(self, parameter: Parameter, index: int, docstring: str = None):
        """
        Create a new parameter schema.

        :param parameter: The parameter to create a schema for
        :param index: The index of the parameter in the function signature
        :param docstring: The docstring for the function containing the parameter
        """
        self.parameter: Parameter = parameter
        self.index: int = index
        self.docstring: str = docstring

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        """
        Determine if this schema can be used for the given parameter.

        :return: True if this schema can be used to parse the given parameter;
        """
        raise NotImplementedError()

    def _get_type(self) -> Union[str, Parameter.empty]:
        """
        Get the type of this parameter, to be added to the JSON schema.
        Return `Parameter.empty` to omit the type from the schema.
        """
        return Parameter.empty

    def _get_items(self) -> Union[str, Parameter.empty]:
        """
        Get the items property to be added to the JSON schema.
        Return `Parameter.empty` to omit the items from the schema.
        """
        return Parameter.empty

    def _get_enum(self) -> Union[list[str], Parameter.empty]:
        """
        Get the enum property to be added to the JSON schema.
        Return `Parameter.empty` to omit the enum from the schema.
        """
        return Parameter.empty

    def _get_description(self) -> Union[str, Parameter.empty]:
        """
        Get the description of this parameter, extracted from the function docstring,
        to be added to the JSON schema. Return `Parameter.empty` to omit the description
        from the schema.
        """
        if self.docstring is None:
            return Parameter.empty

        docstring = " ".join([x.strip() for x in self.docstring.replace("\n", " ").split()])
        params = re.findall(r":param ([^:]*): (.*?)(?=:param|:type|:return|:rtype|$)", docstring)
        for name, desc in params:
            if name == self.parameter.name and desc:
                return desc.strip()

        return Parameter.empty

    def _get_default(self) -> any:
        """
        Get the default value for this parameter, when present, to be added to the JSON schema.
        Return `Parameter.empty` to omit the default value from the schema.
        """
        return self.parameter.default

    def to_json(self) -> dict:
        """
        Return the json schema for this parameter.
        """
        fields = {
            "description": self._get_description,
            "default": self._get_default,
            "items": self._get_items,
            "type": self._get_type,
            "enum": self._get_enum,
        }

        json = dict()

        for field in fields:
            if (value := fields[field]()) != Parameter.empty:
                json[field] = value

        return json

    def parse_value(self, value):
        """
        Convert the given value from the JSON representation to an instance
        that can be passed to the original method as a parameter. Overriding
        methods should check whether the value needs to be converted, and return
        it as is if no conversion is necessary.

        :param value: The value to be converted
        :return: An instance of the type required by the original method
        """
        return value


class ValueTypeSchema(ParameterSchema):
    """
    Parameter schema for value types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return parameter.annotation != Parameter.empty and parameter.annotation.__name__ in TYPE_MAP

    def _get_type(self) -> Union[str, Parameter.empty]:
        return TYPE_MAP[self.parameter.annotation.__name__]


class GenericParameterSchema(ParameterSchema):
    """
    Base class for generic parameter types supporting subscription.
    """

    def _get_sub_type(self) -> Union[str, Parameter.empty]:
        if args := typing.get_args(self.parameter.annotation):
            return TYPE_MAP.get(args[0].__name__, "object")

        return Parameter.empty


class ListTypeParameterSchema(GenericParameterSchema):
    """
    Parameter schema for list (array) types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return parameter.annotation != Parameter.empty and (
            parameter.annotation is list or typing.get_origin(parameter.annotation) is list
        )

    def _get_type(self) -> Union[str, Parameter.empty]:
        return TYPE_MAP["list"]

    def _get_items(self) -> Union[str, Parameter.empty]:
        if (sub_type := super()._get_sub_type()) != Parameter.empty:
            return {"type": sub_type}

        return Parameter.empty


class OptionalTypeParameterSchema(GenericParameterSchema):
    """
    Parameter schema for typing.Optional types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        args = typing.get_args(parameter.annotation)
        return (
            parameter.annotation != parameter.empty
            and typing.get_origin(parameter.annotation) is Union
            and len(args) == 2
            and type(None) in args
        )

    def _get_type(self) -> Union[str, Parameter.empty]:
        return super()._get_sub_type()


class EnumParameterSchema(ParameterSchema):
    """
    Parameter schema for enumeration types.
    """

    def __init__(self, values: list, parameter: Parameter, index: int, docstring: str = None):
        super().__init__(parameter, index, docstring)
        self.enum_values = values

    def _get_type(self) -> Union[str, Parameter.empty]:
        return TYPE_MAP.get(type(self.enum_values[0]).__name__, "object")

    def _get_enum(self) -> Union[list[str], Parameter.empty]:
        return self.enum_values


class EnumTypeParameterSchema(EnumParameterSchema):
    """
    Parameter schema for enum.Enum types.
    """

    def __init__(self, parameter: Parameter, index: int, docstring: str = None):
        values = [e.name for e in parameter.annotation]
        super().__init__(values, parameter, index, docstring)

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != parameter.empty
            and isclass(parameter.annotation)
            and issubclass(parameter.annotation, Enum)
        )

    def parse_value(self, value):
        """
        Convert an enum name to an instance of the enum type.

        :param value: The enum name to be converted
        """
        if value in self.enum_values:
            # Convert to an enum instance
            return self.parameter.annotation[value]

        # The user is invoking the method directly
        return value


class LiteralTypeParameterSchema(EnumParameterSchema):
    """
    Parameter schema for typing.Literal types.
    """

    def __init__(self, parameter: Parameter, index: int, docstring: str = None):
        values = list(typing.get_args(parameter.annotation))
        super().__init__(values, parameter, index, docstring)

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != parameter.empty
            and typing.get_origin(parameter.annotation) is typing.Literal
        )


# Order matters: specific classes should appear before more generic ones;
# for example, ListParameterSchema must precede ValueTypeSchema,
# as they both match list types
PARAMETER_SCHEMAS = [
    OptionalTypeParameterSchema,
    LiteralTypeParameterSchema,
    EnumTypeParameterSchema,
    ListTypeParameterSchema,
    ValueTypeSchema,
]
